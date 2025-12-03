#include <SFML/Graphics.hpp>
#include <SFML/Window.hpp>
#include "json.hpp"
#include "clases.hpp"
#include <vector>
#include <optional>
#include <iostream>
#include <fstream>
#include <random>
#include <chrono>
#include <string>
#include <map>
#include <cstdlib>
#include <ctime>
#include <numeric>

using namespace std;
using json = nlohmann::json;

vector< Ejercito > ElegirEjercitos(Ventana& v) {
	map<string, string> opts;
	opts.insert({ "Tyranidos Pesados", "Ty_Tyrannofex.json" });
	opts.insert({ "Marines Pesados", {"UM_Lancer.json"} });
	opts.insert({ "Tyranidos", {"Ty_patrol.json"} });
	opts.insert({ "Marines", {"UM_patrol.json"} });
	int indice = 0;
	vector < Ejercito > ejercitos;

	v.ventana->clear(sf::Color::Black);
	for (auto i : opts)
	{
		Boton* B = new Boton(sf::Vector2f({ indice * 60, 0 }), sf::Vector2f({ 60, 180 }), i.first);
		v.elementos.push_back(B);
		indice++;
		v.ventana->draw(B->rect);
	}

	while (const std::optional ev = v.ventana->pollEvent())
	{
		if (ejercitos.size() >= 2)
			break;
		if (ev->is<sf::Event::Closed>())
			v.ventana->close();
		else if (const auto* tecla = ev->getIf<sf::Event::KeyPressed>())
			if (tecla->scancode == sf::Keyboard::Scancode::Escape)
				v.ventana->close();
			else if (const auto* click = ev->getIf<sf::Event::MouseButtonPressed>())
			{
				v.PosMouse = sf::Mouse::getPosition(*(v.ventana));
				int PosY = v.PosMouse.y / 60;

				if (click->button == sf::Mouse::Button::Left)
				{
					Boton* B = dynamic_cast<Boton*>(v.elementos[PosY]);
					B->presionado = true;
				}
			}
		for (auto& e : v.elementos)
		{
			Boton* B = dynamic_cast<Boton*>(e);
			if (B->presionado)
			{
				Ejercito nE;
				std::ifstream archivo("sprites/" + opts[B->Texto]);
				json j;
				archivo >> j;
				from_json(j, nE);
				ejercitos.push_back(nE);
				B->presionado = false;
			}
		}
	}

	v.elementos.clear();
	return ejercitos;
}

vector<int> Dados(int n_dados, int Dx, bool ret_num)
{
	vector<int> res_dados;
	for (int i = 0; i < n_dados; i++)
	{
		srand(time(NULL));
		int resultado = (rand() % Dx) + 1;
		res_dados.push_back(resultado);
	}
	return res_dados;
}

int Dados(int n_dados, int Dx)
{
	vector<int> res_dados;
	for (int i = 0; i < n_dados; i++)
	{
		srand(time(NULL));
		int resultado = (rand() % Dx) + 1;
		res_dados.push_back(resultado);
	}
	return accumulate(res_dados.begin(), res_dados.end(), 0);
}

vector<int> AtkDmg_Rand(string nDx)
{
	vector<int> resultados;
	size_t pos_D = nDx.find('D');
	size_t pos_plus = nDx.find('+');

	string sub_s = nDx.substr(0, pos_D);
	int cantidad;

	if (sub_s == "")
		cantidad = 1;
	else
		cantidad = stoi(sub_s);
	cantidad = Dados(cantidad, stoi(nDx.substr(pos_D + 1, pos_plus - pos_D + 1)));
	if (pos_plus != string::npos)
		cantidad += stoi(nDx.substr(pos_plus + 1));
	resultados = Dados(cantidad, stoi(nDx.substr(pos_D + 1, pos_plus - pos_D + 1)), false);
	return resultados;
}

int AtkDmg_Rand(string nDx, bool dmg)
{
	size_t pos_D = nDx.find('D');
	size_t pos_plus = nDx.find('+');

	string sub_s = nDx.substr(0, pos_D);
	int cantidad;

	if (sub_s == "")
		cantidad = 1;
	else
		cantidad = stoi(sub_s);
	cantidad = Dados(cantidad, stoi(nDx.substr(pos_D + 1, pos_plus - pos_D + 1)));
	if (pos_plus != string::npos)
		cantidad += stoi(nDx.substr(pos_plus + 1));
	return cantidad;
}

vector<int> RepFallos(vector<int> tiradas, int val, int Dx)
{
	vector<int> exito;
	vector<int> nuevos;
	for (auto t : tiradas)
		if (t >= val)
			exito.push_back(t);
	nuevos = Dados(tiradas.size() - exito.size(), Dx, false);
	exito.insert(exito.end(), nuevos.begin(), nuevos.end());
	return exito;
}

int RepFallos(vector<int> tiradas, int val, int Dx, bool ret_num)
{
	vector<int> exito;
	vector<int> nuevos;
	for (auto t : tiradas)
		if (t >= val)
			exito.push_back(t);
	nuevos = Dados(tiradas.size() - exito.size(), Dx, false);
	exito.insert(exito.end(), nuevos.begin(), nuevos.end());
	return accumulate(exito.begin(), exito.end(), 0);
}

void Aumentar_PC(vector<Ejercito> Ejs)
{
	for (auto& ej : Ejs)
		ej.pc += 1;
	return;
}

void Aumentar_Mov_Atk(Ejercito Ej)
{
	for (auto& u : Ej.unidades)
	{
		u.mov = 3;
		u.atk = 3;
	}
	return;
}


void esperarConfirmacion(Ventana& v)
{
	while (true)
	{
		while (const auto event = v.ventana->pollEvent())
		{
			if (event->is<sf::Event::Closed>())
			{
				v.ventana->close();
				return;
			}

			if (event->is<sf::Event::KeyPressed>() ||
				event->is<sf::Event::MouseButtonPressed>())
			{
				return; // Usuario confirma
			}
		}

		v.ventana->clear(sf::Color::Black);
		v.dibujarElementos();
		v.ventana->display();
	}
}

void Shock_Test(Unidad& U, Ventana& v)
{
	v.ventana->clear(sf::Color::Black);
	if ((U.miembros.size() < U.nm / 2) && (U.nm != 1))
	{
		int mayor = 0;
		for (auto& m : U.miembros)
			if (m.stats_map["Liderazgo"] > mayor)
				mayor = m.stats_map["Liderazgo"];
		int prueba = Dados(2, 6);
		TextBox* T = dynamic_cast<TextBox*>(*(v.elementos.end()));
		if (prueba < mayor)
		{
			U.shock = true;
			T->setText("Unidad " + U.nombre + " esta en shock!");
			esperarConfirmacion(v);
		}
		else
		{
			U.shock = false;
			T->setText("Unidad " + U.nombre + " supera la prueba de shock.");
			esperarConfirmacion(v);
		}
	}
	else if (U.nm == 1 && U.miembros[0].dmg > U.miembros[0].stats_map["Heridas"] / 2)
	{
		int prueba = Dados(2, 6);
		TextBox* T = dynamic_cast<TextBox*>(*(v.elementos.end()));
		if (prueba < U.miembros[0].stats_map["Liderazgo"])
		{
			U.shock = true;
			T->setText("Miniatura " + U.miembros[0].nombre + " esta en shock!");
			esperarConfirmacion(v);
		}
		else
		{
			U.shock = false;
			T->setText("Miniatura " + U.miembros[0].nombre + " supera la prueba de shock.");
			esperarConfirmacion(v);
		}
	}
	else
	{
		U.shock = false;
		TextBox* T = dynamic_cast<TextBox*>(*(v.elementos.end()));
		T->setText("Unidad " + U.nombre + " no necesita prueba de shock.");
		esperarConfirmacion(v);
	}
}

bool puntoEnCirculo(const sf::Vector2f& punto, const sf::CircleShape& c)
{
	sf::Vector2f centro = c.getPosition() + c.getOrigin();
	float dx = punto.x - centro.x;
	float dy = punto.y - centro.y;
	float distancia2 = dx * dx + dy * dy;
	float r = c.getRadius();

	return distancia2 <= (r * r);
}

int Selec_mini(Ventana& v_Monitor, Ventana& v_Tablero, Unidad& u)
{
	TextBox* mensaje = dynamic_cast<TextBox*>(*(v_Monitor.elementos.end()));
	mensaje->setText("Seleccione una miniatura...");

	while (v_Tablero.ventana->isOpen())
	{
		while (const auto event = v_Tablero.ventana->pollEvent())
		{
			if (event->is<sf::Event::Closed>())
			{
				v_Tablero.ventana->close();
				return -1;
			}

			if (const auto* mouse = event->getIf<sf::Event::MouseButtonPressed>())
			{
				if (mouse->button == sf::Mouse::Button::Left)
				{
					sf::Vector2f clickPos = {
						static_cast<float>(mouse->position.x),
						static_cast<float>(mouse->position.y)
					};

					// Revisar todos los circulos
					for (int i = 0; i < u.circulos.size(); i++)
					{
						const sf::CircleShape& c = u.circulos[i];

						if (puntoEnCirculo(clickPos, c))
						{
							// Seleccion exitosa
							mensaje->setText("Seleccionado: " + u.miembros[i].nombre);
							esperarConfirmacion(v_Tablero);
							return i;
						}
					}
				}
			}
		}

		// Dibujar la ventana normalmente
		v_Tablero.ventana->clear(sf::Color::White);
		v_Tablero.dibujarElementos();
		v_Tablero.ventana->display();

		v_Monitor.ventana->clear(sf::Color::Black);
		v_Monitor.dibujarElementos();
		v_Monitor.ventana->display();
	}

	return -1; // Si se cerro la ventana
}

void RepDmg(Ventana& v_monitor, Ventana& v_tablero, Unidad& blanco, int& dano, bool presicion = false)
{
	while (dano >= 1)
	{
		int danada = Selec_mini(v_monitor, v_tablero, blanco);
		if (danada == -1)
		{
			dano = 0;
			return;
		}
		int Qt_dmg = blanco.miembros[danada].stats_map["Heridas"].get<int>() - blanco.miembros[danada].dmg;
		TextBox* T = dynamic_cast<TextBox*>(*(v_monitor.elementos.end()));
		if (dano >= Qt_dmg)
		{
			T->setText(blanco.miembros[danada].Recibir_Dano(v_monitor, Qt_dmg, blanco.habilidades));
			esperarConfirmacion(v_monitor);
			dano -= Qt_dmg;
			blanco.eliminar_muertos();
			continue;
		}
		else
		{
			blanco.miembros[danada].Recibir_Dano(v_monitor, dano, blanco.habilidades);
			T->setText(blanco.miembros[danada].nombre + " ha recibido " + to_string(blanco.miembros[danada].dmg) + " de dano.");
			esperarConfirmacion(v_monitor);
			dano = 0;
			continue;
		}
	}
	return;
}

Unidad Selec_Blanco(Ventana& v_monitor, Unidad& u, string& accion, Ejercito& Ejer_Enem, bool Indirecta = false)
{
	int indice = 0;

	// Depurar ejercito enemigo antes de seleccionar
	Ejer_Enem.eliminar_unidades();

	TextBox* mensaje = dynamic_cast<TextBox*>(*(v_monitor.elementos.end()));
	mensaje->setText("Seleccione un objetivo para: " + accion);

	// Bucle principal de seleccion
	while (v_monitor.ventana->isOpen())
	{
		// Procesar eventos
		while (const auto event = v_monitor.ventana->pollEvent())
		{
			if (event->is<sf::Event::Closed>())
			{
				v_monitor.ventana->close();
				return Unidad{}; // Devuelve objeto vacio
			}

			if (const auto* mouse = event->getIf<sf::Event::MouseButtonPressed>())
			{
				if (mouse->button == sf::Mouse::Button::Left)
				{
					sf::Vector2f clickPos = {
						static_cast<float>(mouse->position.x),
						static_cast<float>(mouse->position.y)
					};

					// Recorrer todas las unidades enemigas
					for (Unidad& objetivo : Ejer_Enem.unidades)
					{
						// Revisar cada miniatura (circulo)
						for (int i = 0; i < objetivo.circulos.size(); i++)
						{
							const sf::CircleShape& c = objetivo.circulos[i];

							if (puntoEnCirculo(clickPos, c))
							{
								// Un objetivo fue clickeado
								mensaje->setText(
									"Objetivo seleccionado: " + objetivo.nombre
								);

								esperarConfirmacion(v_monitor);

								return objetivo; //Se devuelve la unidad completa
							}
						}
					}
				}
			}
		}

		// Refrescar ventana del monitor
		v_monitor.ventana->clear(sf::Color::Black);
		v_monitor.dibujarElementos();
		v_monitor.ventana->display();
	}

	return Unidad{}; // Si se cerro ventana
}

float Visible(Ventana& v_tablero,
	Unidad& A, Unidad& B)
{
	// Primero verificar que ambas unidades tengan miniaturas
	if (A.circulos.empty() || B.circulos.empty())
		return false;

	// Obtener rectangulos de obstaculos desde el tablero
	std::vector<sf::FloatRect> obstaculos;

	for (Elemento* e : v_tablero.elementos)
	{
		// Si el elemento tiene un metodo getRect(), usalo
		if (auto* obs = dynamic_cast<Obstaculo*>(e))
			obstaculos.push_back(obs->getRect());
	}

	// Comprobacion de linea de vision entre miniaturas
	for (const auto& cA : A.circulos)
	{
		sf::Vector2f pA = cA.getPosition() + cA.getOrigin();

		for (const auto& cB : B.circulos)
		{
			sf::Vector2f pB = cB.getPosition() + cB.getOrigin();

			// Crear un rectangulo fino para representar la linea
			sf::RectangleShape ray;
			float dx = pB.x - pA.x;
			float dy = pB.y - pA.y;
			float distancia = std::sqrt(dx * dx + dy * dy);

			ray.setSize(sf::Vector2f(distancia, 1.f)); // linea fina
			ray.setPosition(pA);

			sf::Angle angulo = sf::radians(atan2(dy, dx) * 180.f / 3.14159265f);
			ray.setRotation(angulo);

			bool bloqueado = false;

			for (const auto& obs : obstaculos)
			{
				if (ray.getGlobalBounds().findIntersection(obs))
				{
					bloqueado = true;
					break;
				}
			}

			if (!bloqueado)
			{
				// Linea de vision verdadera
				return distancia / 25.4f;
			}
		}
	}

	// Si todos los rayos estan bloqueados
	return -1.f;
}

int main()
{
	// Inicialización de ventanas
	Ventana v_tablero(800, 600, "WHmmatic: Tablero");
	Ventana v_monitor(400, 600, "WHmmatic: Monitor");

	// Agregar un TextBox a la ventana de monitor para mensajes
	TextBox* msgBox = new TextBox(
		{ 400.f, 50.f },
		{ 0.f, 0.f },
		"Seleccione un ejército..."
	);
	v_monitor.elementos.push_back(msgBox);

	// --- Selección de Ejércitos ---
	vector<Ejercito> ejercitos;

	while (ejercitos.size() < 2 && v_monitor.ventana->isOpen())
	{
		ejercitos = ElegirEjercitos(v_monitor);

		v_monitor.ventana->clear(sf::Color::Black);
		v_monitor.dibujarElementos();
		v_monitor.ventana->display();
	}

	if (ejercitos.size() != 2)
	{
		cout << "Se necesita seleccionar 2 ejércitos para iniciar." << endl;
		return 0;
	}

	// Inicialización de Unidades
	for (auto& ejercito : ejercitos)
	{
		for (auto& unidad : ejercito.unidades)
		{
			unidad.crear_circulos();
			for (const auto& circulo : unidad.circulos)
			{
				// Agregar las miniaturas al tablero
				v_tablero.elementos.push_back(new Elemento(circulo));
			}
		}
	}

	int ronda = 1;
	int turno_jugador = 0; // 0 para el jugador 1, 1 para el jugador 2
	bool juego_terminado = false;

	while (v_tablero.ventana->isOpen() && !juego_terminado)
	{
		// 1. Fase de Comando
		msgBox->setText("Ronda " + to_string(ronda) + " - Jugador " + to_string(turno_jugador + 1) + ": Fase de Comando");
		esperarConfirmacion(v_monitor);
		Aumentar_PC(ejercitos);

		// 2. Fase de Movimiento
		msgBox->setText("Fase de Movimiento. Seleccione unidad para mover/activar.");
		esperarConfirmacion(v_monitor);
		// Lógica de Movimiento y activación
		Aumentar_Mov_Atk(ejercitos[turno_jugador]);

		// 3. Fase de Disparo
		msgBox->setText("Fase de Disparo. Seleccione unidad para disparar.");
		esperarConfirmacion(v_monitor);

		// Ejemplo de lógica de disparo
		Unidad* unidad_atacante = &ejercitos[turno_jugador].unidades.front();
		Unidad* unidad_defensora = &ejercitos[1 - turno_jugador].unidades.front();
		string accion = "Disparar";

		// 4. Fase de Carga 
		msgBox->setText("Fase de Carga.");
		esperarConfirmacion(v_monitor);

		// 5. Fase de Combate
		msgBox->setText("Fase de Combate.");
		esperarConfirmacion(v_monitor);

		// 6. Prueba de Choque
		msgBox->setText("Prueba de Shock.");
		esperarConfirmacion(v_monitor);
		// Iterar sobre unidades que hayan perdido miniaturas y aplicar Shock_Test

		// 7. Limpieza
		ejercitos[0].eliminar_unidades();
		ejercitos[1].eliminar_unidades();

		// Verificar fin de juego
		if (ejercitos[0].unidades.empty() || ejercitos[1].unidades.empty() || ronda >= 5)
		{
			juego_terminado = true;
		}

		// Cambiar de turno o avanzar ronda
		if (turno_jugador == 1)
		{
			ronda++;
			turno_jugador = 0;
		}
		else
		{
			turno_jugador = 1;
		}

		// Procesamiento de eventos
		sf::Event event;
		while (v_tablero.ventana->pollEvent(event))
		{
			if (event.type == sf::Event::Closed)
				v_tablero.ventana->close();
		}
		while (v_monitor.ventana->pollEvent(event))
		{
			if (event.type == sf::Event::Closed)
				v_monitor.ventana->close();
		}

		// Dibujar todo
		v_tablero.ventana->clear(sf::Color::White);
		v_tablero.dibujarElementos();
		v_tablero.ventana->display();

		v_monitor.ventana->clear(sf::Color::Black);
		v_monitor.dibujarElementos();
		v_monitor.ventana->display();
	}

	// Fin del Juego
	if (ejercitos[0].unidades.empty() && !ejercitos[1].unidades.empty())
	{
		msgBox->setText("¡Ejército " + ejercitos[1].faccion + " ha ganado!");
	}
	else if (ejercitos[1].unidades.empty() && !ejercitos[0].unidades.empty())
	{
		msgBox->setText("¡Ejército " + ejercitos[0].faccion + " ha ganado!");
	}
	else
	{
		// Lógica para determinar el ganador si se acaba el número de rondas
		msgBox->setText("Fin de partida. Empate o definir por puntos.");
	}

	esperarConfirmacion(v_monitor); // Mantener la ventana abierta hasta confirmación

	// Limpiar la memoria
	delete msgBox;

	return 0;
}
