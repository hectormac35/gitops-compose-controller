import json

from state_store import MAX_HISTORIAL, cargar_estado, guardar_evento


def test_estado_inicial_si_no_existe(tmp_path):
    assert cargar_estado(str(tmp_path / "no-existe.json"))["ultimo_evento"] == "Inicializado"


def test_recupera_estado_si_el_json_esta_danado(tmp_path):
    archivo = tmp_path / "estado.json"
    archivo.write_text('{"ultimo_commit": "abc", ')  # escritura cortada
    assert cargar_estado(str(archivo))["ultimo_evento"] == "Inicializado"


def test_guarda_y_registra_en_historial(tmp_path):
    archivo = str(tmp_path / "estado.json")
    guardar_evento(archivo, {"ultimo_commit": "a" * 40, "ultimo_evento": "Aplicado correctamente"}, registrar=True)
    guardar_evento(archivo, {"ultimo_evento": "Sin cambios"})  # no se registra
    datos = json.loads(open(archivo).read())
    assert datos["ultimo_evento"] == "Sin cambios"
    assert [e["evento"] for e in datos["historial"]] == ["Aplicado correctamente"]
    assert datos["historial"][0]["commit"] == "a" * 12


def test_historial_limitado_y_mas_reciente_primero(tmp_path):
    archivo = str(tmp_path / "estado.json")
    for i in range(MAX_HISTORIAL + 5):
        guardar_evento(archivo, {"ultimo_evento": f"evento {i}"}, registrar=True)
    historial = cargar_estado(archivo)["historial"]
    assert len(historial) == MAX_HISTORIAL
    assert historial[0]["evento"] == f"evento {MAX_HISTORIAL + 4}"


def test_no_deja_ficheros_temporales(tmp_path):
    archivo = str(tmp_path / "estado.json")
    for i in range(5):
        guardar_evento(archivo, {"ultimo_evento": str(i)})
    assert [p.name for p in tmp_path.iterdir()] == ["estado.json"]


def test_descarta_el_campo_antiguo_docker_compose_ps(tmp_path):
    archivo = tmp_path / "estado.json"
    archivo.write_text(json.dumps({"ultimo_commit": "abc", "docker_compose_ps": "NAME IMAGE ..."}))
    estado = cargar_estado(str(archivo))
    assert "docker_compose_ps" not in estado and estado["ultimo_commit"] == "abc"
