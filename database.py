import os
import json
import psycopg2
import psycopg2.extras
from datetime import datetime

class Database:
    def __init__(self):
        url = os.environ["DATABASE_URL"]
        # Railway a veces da URLs con "postgres://" — psycopg2 necesita "postgresql://"
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        self.conn = psycopg2.connect(url, cursor_factory=psycopg2.extras.RealDictCursor)
        self.conn.autocommit = False
        self.create_tables()

    def _cur(self):
        """Devuelve un cursor fresco, reconectando si la conexión se cayó."""
        try:
            self.conn.isolation_level  # ping rápido
        except Exception:
            url = os.environ["DATABASE_URL"]
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql://", 1)
            self.conn = psycopg2.connect(url, cursor_factory=psycopg2.extras.RealDictCursor)
            self.conn.autocommit = False
        return self.conn.cursor()

    def _commit(self):
        self.conn.commit()

    def create_tables(self):
        c = self._cur()
        c.execute("""
        CREATE TABLE IF NOT EXISTS jugadores (
            discord_id TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            nivel INTEGER DEFAULT 1,
            exp INTEGER DEFAULT 0,
            vida INTEGER DEFAULT 100,
            vida_max INTEGER DEFAULT 100,
            ataque INTEGER DEFAULT 10,
            defensa INTEGER DEFAULT 5,
            velocidad INTEGER DEFAULT 8,
            zona TEXT DEFAULT 'refugio',
            tapas INTEGER DEFAULT 50,
            kills INTEGER DEFAULT 0,
            muertes INTEGER DEFAULT 0,
            inventario TEXT DEFAULT '{}',
            estado TEXT DEFAULT 'vivo',
            creado_en TIMESTAMP DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS misiones (
            id SERIAL PRIMARY KEY,
            titulo TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            tipo TEXT NOT NULL,
            objetivo_cantidad INTEGER DEFAULT 1,
            recompensa_tapas INTEGER DEFAULT 0,
            recompensa_exp INTEGER DEFAULT 0,
            recompensa_item TEXT DEFAULT '',
            zona_requerida TEXT DEFAULT '',
            activa INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS misiones_jugador (
            discord_id TEXT,
            mision_id INTEGER,
            progreso INTEGER DEFAULT 0,
            completada INTEGER DEFAULT 0,
            aceptada_en TIMESTAMP DEFAULT NOW(),
            PRIMARY KEY (discord_id, mision_id)
        );

        CREATE TABLE IF NOT EXISTS eventos_log (
            id SERIAL PRIMARY KEY,
            discord_id TEXT,
            tipo TEXT,
            descripcion TEXT,
            fecha TIMESTAMP DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS bases (
            discord_id TEXT PRIMARY KEY,
            nombre TEXT DEFAULT 'Base sin nombre',
            vida_muro INTEGER DEFAULT 0,
            vida_muro_max INTEGER DEFAULT 0,
            estructuras TEXT DEFAULT '{}',
            almacen TEXT DEFAULT '{}',
            ultimo_ataque TIMESTAMP DEFAULT NULL,
            ataques_recibidos INTEGER DEFAULT 0,
            ataques_repelidos INTEGER DEFAULT 0,
            canal_notif TEXT DEFAULT NULL
        );

        CREATE TABLE IF NOT EXISTS ataques_log (
            id SERIAL PRIMARY KEY,
            discord_id TEXT,
            oleada_nivel INTEGER,
            oleada_nombre TEXT,
            resultado TEXT,
            dano_recibido INTEGER,
            recursos_perdidos TEXT DEFAULT '{}',
            tapas_perdidas INTEGER DEFAULT 0,
            fecha TIMESTAMP DEFAULT NOW()
        );
        """)
        self._commit()
        self._seed_misiones()

    def _seed_misiones(self):
        c = self._cur()
        c.execute("SELECT COUNT(*) as n FROM misiones")
        if c.fetchone()["n"] == 0:
            misiones = [
                ("Limpieza Inicial", "Elimina 3 zombies en el hospital", "matar_zombies", 3, 30, 50, "venda", "hospital"),
                ("Provisiones Urgentes", "Consigue 5 unidades de comida", "recolectar_comida", 5, 50, 80, "mochila_grande", "supermercado"),
                ("Munición Escasa", "Recolecta munición en la armería", "recolectar_municion", 10, 40, 60, "pistola", "armeria"),
                ("Explorador Novato", "Explora 4 zonas diferentes", "explorar_zonas", 4, 60, 100, "mapa_detallado", ""),
                ("Carnicero", "Elimina 10 zombies en cualquier zona", "matar_zombies", 10, 100, 200, "hacha", ""),
                ("Superviviente", "Sobrevive 5 exploraciones sin morir", "sobrevivir_exploraciones", 5, 150, 250, "chaleco_kevlar", ""),
                ("El Último Bastión", "Defiende el refugio de 15 zombies", "matar_zombies", 15, 200, 350, "rifle", "refugio"),
                ("Buscador de Recursos", "Vende items por valor de 100 tapas", "vender_items", 100, 80, 120, "mochila_tactica", ""),
            ]
            c.executemany(
                "INSERT INTO misiones (titulo, descripcion, tipo, objetivo_cantidad, recompensa_tapas, recompensa_exp, recompensa_item, zona_requerida) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                misiones
            )
            self._commit()

    # ── JUGADOR ──────────────────────────────────────────────
    def get_jugador(self, discord_id):
        c = self._cur()
        c.execute("SELECT * FROM jugadores WHERE discord_id=%s", (str(discord_id),))
        row = c.fetchone()
        if row:
            d = dict(row)
            d["inventario"] = json.loads(d["inventario"])
            return d
        return None

    def crear_jugador(self, discord_id, nombre):
        inventario_inicial = json.dumps({"venda": 2, "comida": 3, "municion": 10})
        c = self._cur()
        c.execute(
            "INSERT INTO jugadores (discord_id, nombre, inventario) VALUES (%s,%s,%s) ON CONFLICT DO NOTHING",
            (str(discord_id), nombre, inventario_inicial)
        )
        self._commit()

    def update_jugador(self, discord_id, **kwargs):
        if "inventario" in kwargs:
            kwargs["inventario"] = json.dumps(kwargs["inventario"])
        sets = ", ".join(f"{k}=%s" for k in kwargs)
        vals = list(kwargs.values()) + [str(discord_id)]
        c = self._cur()
        c.execute(f"UPDATE jugadores SET {sets} WHERE discord_id=%s", vals)
        self._commit()

    def add_exp(self, discord_id, cantidad):
        jugador = self.get_jugador(discord_id)
        if not jugador:
            return False, 0
        nueva_exp = jugador["exp"] + cantidad
        nuevo_nivel = jugador["nivel"]
        exp_para_nivel = nuevo_nivel * 100
        subio_nivel = False
        if nueva_exp >= exp_para_nivel:
            nueva_exp -= exp_para_nivel
            nuevo_nivel += 1
            subio_nivel = True
            nueva_vida_max = jugador["vida_max"] + 20
            self.update_jugador(discord_id,
                nivel=nuevo_nivel, exp=nueva_exp,
                vida_max=nueva_vida_max, vida=nueva_vida_max,
                ataque=jugador["ataque"] + 3,
                defensa=jugador["defensa"] + 2
            )
        else:
            self.update_jugador(discord_id, exp=nueva_exp)
        return subio_nivel, nuevo_nivel

    def add_item_inventario(self, discord_id, item, cantidad=1):
        jugador = self.get_jugador(discord_id)
        if not jugador:
            return
        inv = jugador["inventario"]
        inv[item] = inv.get(item, 0) + cantidad
        self.update_jugador(discord_id, inventario=inv)

    def remove_item_inventario(self, discord_id, item, cantidad=1):
        jugador = self.get_jugador(discord_id)
        if not jugador:
            return False
        inv = jugador["inventario"]
        if inv.get(item, 0) < cantidad:
            return False
        inv[item] -= cantidad
        if inv[item] <= 0:
            del inv[item]
        self.update_jugador(discord_id, inventario=inv)
        return True

    # ── MISIONES ─────────────────────────────────────────────
    def get_misiones(self):
        c = self._cur()
        c.execute("SELECT * FROM misiones WHERE activa=1")
        return [dict(r) for r in c.fetchall()]

    def get_mision(self, mision_id):
        c = self._cur()
        c.execute("SELECT * FROM misiones WHERE id=%s", (mision_id,))
        row = c.fetchone()
        return dict(row) if row else None

    def aceptar_mision(self, discord_id, mision_id):
        c = self._cur()
        c.execute("SELECT 1 FROM misiones_jugador WHERE discord_id=%s AND mision_id=%s",
                  (str(discord_id), mision_id))
        if c.fetchone():
            return False
        c.execute("INSERT INTO misiones_jugador (discord_id, mision_id) VALUES (%s,%s)",
                  (str(discord_id), mision_id))
        self._commit()
        return True

    def get_misiones_jugador(self, discord_id):
        c = self._cur()
        c.execute("""
            SELECT m.*, mj.progreso, mj.completada
            FROM misiones m
            JOIN misiones_jugador mj ON m.id = mj.mision_id
            WHERE mj.discord_id=%s AND mj.completada=0
        """, (str(discord_id),))
        return [dict(r) for r in c.fetchall()]

    def actualizar_progreso_mision(self, discord_id, tipo, cantidad=1):
        c = self._cur()
        c.execute("""
            SELECT mj.mision_id, mj.progreso, m.objetivo_cantidad
            FROM misiones_jugador mj
            JOIN misiones m ON m.id = mj.mision_id
            WHERE mj.discord_id=%s AND mj.completada=0 AND m.tipo=%s
        """, (str(discord_id), tipo))
        activas = c.fetchall()
        completadas = []
        for row in activas:
            nuevo_progreso = row["progreso"] + cantidad
            if nuevo_progreso >= row["objetivo_cantidad"]:
                c.execute("UPDATE misiones_jugador SET progreso=%s, completada=1 WHERE discord_id=%s AND mision_id=%s",
                          (row["objetivo_cantidad"], str(discord_id), row["mision_id"]))
                completadas.append(row["mision_id"])
            else:
                c.execute("UPDATE misiones_jugador SET progreso=%s WHERE discord_id=%s AND mision_id=%s",
                          (nuevo_progreso, str(discord_id), row["mision_id"]))
        self._commit()
        return completadas

    def entregar_mision(self, discord_id, mision_id):
        c = self._cur()
        c.execute("SELECT * FROM misiones_jugador WHERE discord_id=%s AND mision_id=%s AND completada=1",
                  (str(discord_id), mision_id))
        if not c.fetchone():
            return None
        mision = self.get_mision(mision_id)
        c.execute("DELETE FROM misiones_jugador WHERE discord_id=%s AND mision_id=%s",
                  (str(discord_id), mision_id))
        self._commit()
        return mision

    def log_evento(self, discord_id, tipo, descripcion):
        c = self._cur()
        c.execute("INSERT INTO eventos_log (discord_id, tipo, descripcion) VALUES (%s,%s,%s)",
                  (str(discord_id), tipo, descripcion))
        self._commit()

    # ── BASES ─────────────────────────────────────────────────
    def get_base(self, discord_id):
        c = self._cur()
        c.execute("SELECT * FROM bases WHERE discord_id=%s", (str(discord_id),))
        row = c.fetchone()
        if row:
            d = dict(row)
            d["estructuras"] = json.loads(d["estructuras"])
            d["almacen"] = json.loads(d["almacen"])
            return d
        return None

    def crear_base(self, discord_id, nombre):
        estructuras_init = json.dumps({e: 0 for e in
            ["muro", "torretas", "almacen", "generador", "hospital_base", "laboratorio"]})
        c = self._cur()
        c.execute(
            "INSERT INTO bases (discord_id, nombre, estructuras, almacen) VALUES (%s,%s,%s,%s) ON CONFLICT DO NOTHING",
            (str(discord_id), nombre, estructuras_init, "{}")
        )
        self._commit()

    def update_base(self, discord_id, **kwargs):
        if "estructuras" in kwargs:
            kwargs["estructuras"] = json.dumps(kwargs["estructuras"])
        if "almacen" in kwargs:
            kwargs["almacen"] = json.dumps(kwargs["almacen"])
        sets = ", ".join(f"{k}=%s" for k in kwargs)
        vals = list(kwargs.values()) + [str(discord_id)]
        c = self._cur()
        c.execute(f"UPDATE bases SET {sets} WHERE discord_id=%s", vals)
        self._commit()

    def get_todas_las_bases(self):
        c = self._cur()
        c.execute("SELECT * FROM bases WHERE canal_notif IS NOT NULL")
        result = []
        for row in c.fetchall():
            d = dict(row)
            d["estructuras"] = json.loads(d["estructuras"])
            d["almacen"] = json.loads(d["almacen"])
            result.append(d)
        return result

    def add_item_almacen(self, discord_id, item_id, cantidad=1):
        base = self.get_base(discord_id)
        if not base:
            return False
        almacen = base["almacen"]
        almacen[item_id] = almacen.get(item_id, 0) + cantidad
        self.update_base(discord_id, almacen=almacen)
        return True

    def remove_item_almacen(self, discord_id, item_id, cantidad=1):
        base = self.get_base(discord_id)
        if not base:
            return False
        almacen = base["almacen"]
        if almacen.get(item_id, 0) < cantidad:
            return False
        almacen[item_id] -= cantidad
        if almacen[item_id] <= 0:
            del almacen[item_id]
        self.update_base(discord_id, almacen=almacen)
        return True

    def log_ataque(self, discord_id, oleada_nivel, oleada_nombre, resultado, dano, recursos_perdidos, tapas_perdidas):
        c = self._cur()
        c.execute(
            "INSERT INTO ataques_log (discord_id, oleada_nivel, oleada_nombre, resultado, dano_recibido, recursos_perdidos, tapas_perdidas) VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (str(discord_id), oleada_nivel, oleada_nombre, resultado, dano, json.dumps(recursos_perdidos), tapas_perdidas)
        )
        self._commit()

    def get_historial_ataques(self, discord_id, limit=5):
        c = self._cur()
        c.execute("SELECT * FROM ataques_log WHERE discord_id=%s ORDER BY fecha DESC LIMIT %s",
                  (str(discord_id), limit))
        result = []
        for row in c.fetchall():
            d = dict(row)
            d["recursos_perdidos"] = json.loads(d["recursos_perdidos"])
            result.append(d)
        return result
