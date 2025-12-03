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
#include <set>

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
		Boton* B = new Boton(sf::Vector2f({ 0.f, indice * 60.f }), sf::Vector2f({ 60.f, 180.f }), i.first);
		v.Botones.push_back(B);
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
					Boton* B = dynamic_cast<Boton*>(v.Botones[PosY]);
					B->presionado = true;
				}
			}
		for (auto& B : v.Botones)
		{
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

	v.Botones.clear();
	return ejercitos;
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
		TextBox* T = v.TextBoxes[v.TextBoxes.size()-1];
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
		TextBox* T = v.TextBoxes[v.TextBoxes.size() - 1];
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
		TextBox* T = v.TextBoxes[v.TextBoxes.size() - 1];
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
	TextBox* mensaje = v_Monitor.TextBoxes[v_Monitor.TextBoxes.size()-1];
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
						const sf::CircleShape& c = u.circulos[i].circle;

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
		TextBox* T = v_monitor.TextBoxes[v_monitor.TextBoxes.size()-1];
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

Unidad* Selec_Blanco(Ventana& v_monitor, Unidad& u, const string& accion, Ejercito& Ejer_Enem)
{
	int indice = 0;

	// Depurar ejercito enemigo antes de seleccionar
	Ejer_Enem.eliminar_unidades();

	TextBox* mensaje = v_monitor.TextBoxes[v_monitor.TextBoxes.size()-1];
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
				return nullptr; // Devuelve objeto vacio
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
							const sf::CircleShape& c = objetivo.circulos[i].circle;

							if (puntoEnCirculo(clickPos, c))
							{
								// Un objetivo fue clickeado
								mensaje->setText(
									"Objetivo seleccionado: " + objetivo.nombre
								);

								esperarConfirmacion(v_monitor);

								return &objetivo; //Se devuelve el puntero a la unidad completa
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

	return nullptr; // Si se cerro ventana
}

float Visible(Ventana& v_tablero,
	Unidad& A, Unidad& B)
{
	// Primero verificar que ambas unidades tengan miniaturas
	if (A.circulos.empty() || B.circulos.empty())
		return false;

	// Obtener rectangulos de obstaculos desde el tablero
	std::vector<sf::FloatRect> obstaculos;

	for (auto* o : v_tablero.Obstaculos)
			obstaculos.push_back(o->getRect());

	// Comprobacion de linea de vision entre miniaturas
	for (const auto& cA : A.circulos)
	{
		sf::Vector2f pA = cA.circle.getPosition() + cA.circle.getOrigin();

		for (const auto& cB : B.circulos)
		{
			sf::Vector2f pB = cB.circle.getPosition() + cB.circle.getOrigin();

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

bool allTrue(const vector<bool>& vec)
{
	for (bool b : vec)
		if (!b)
			return false;
	return true;
}

int Selec_Arma(Ventana& v_tablero, Unidad& u, Individuo& i, bool a_distancia)
{
	const auto& armas_originales = a_distancia ? i.rango : i.mele;

	// Crear una lista de nombres con "No disparar" al final
	std::vector<std::string> nombres;
	nombres.reserve(armas_originales.size() + 1);

	for (const auto& arma : armas_originales)
		nombres.push_back(arma.nombre);

	nombres.push_back("No disparar");   // Opción final

	int indice = 0; // índice dentro del vector nombres

	TextBox selector({ 140.f, 30.f }, { 0, 0 }, nombres[indice]);

	if (!u.circulos.empty())
	{
		sf::Vector2f pos = u.circulos[0].circle.getPosition();
		selector.setPosition({ pos.x + 30.f, pos.y - 20.f });
	}

	while (v_tablero.ventana->isOpen())
	{
		while (const auto event = v_tablero.ventana->pollEvent())
		{
			if (event->is<sf::Event::Closed>())
			{
				v_tablero.ventana->close();
				return -1;
			}

			// ----------------- Navegación de armas -----------------
			if (const auto* key = event->getIf<sf::Event::KeyPressed>())
			{
				// Flecha izquierda
				if (key->scancode == sf::Keyboard::Scancode::Left)
				{
					indice--;
					if (indice < 0) indice = nombres.size() - 1;
					selector.setText(nombres[indice]);
				}

				// Flecha derecha
				if (key->scancode == sf::Keyboard::Scancode::Right)
				{
					indice++;
					if (indice >= nombres.size()) indice = 0;
					selector.setText(nombres[indice]);
				}
			}

			// ----------------- Confirmación -----------------
			if (const auto* mouse = event->getIf<sf::Event::MouseButtonPressed>())
			{
				if (mouse->button == sf::Mouse::Button::Left)
				{
					// Caso "No disparar"
					if (nombres[indice] == "No disparar")
					{
						return -1;
					}

					// Caso arma normal: devolver índice original
					return indice;
				}
			}
		}

		v_tablero.ventana->clear(sf::Color::Black);
		v_tablero.dibujarElementos();

		v_tablero.ventana->draw(*(selector.getBox()));
		v_tablero.ventana->draw(*(selector.getText()));
		v_tablero.ventana->display();
	}

	return -1;
}

int Repetida(Arma& a, Unidad& u)
{
	string nombre_a = a.nombre;
	int n = 0;
	for (auto& m : u.miembros)
	{
		for (auto& ar : m.rango)
			if (ar.nombre == nombre_a && !(ar.usado))
				n += 1;
		for (auto& ar : m.mele)
			if (ar.nombre == nombre_a && !(ar.usado))
				n += 1;
	}
	return n;
}

bool Selec_SN(Ventana& v_monitor, const std::string& pregunta)
{
	// Obtener el TextBox final del monitor
	TextBox* mensaje = (*(v_monitor.TextBoxes.end()-1));

	// Texto inicial: pregunta + instrucciones
	mensaje->setText(pregunta + "\n[S] Sí   /   [N] No");

	while (v_monitor.ventana->isOpen())
	{
		// Leer eventos
		while (const auto event = v_monitor.ventana->pollEvent())
		{
			if (event->is<sf::Event::Closed>())
			{
				v_monitor.ventana->close();
				return false;
			}

			if (const auto* key = event->getIf<sf::Event::KeyPressed>())
			{
				// Tecla S → Sí
				if (key->scancode == sf::Keyboard::Scancode::S)
					return true;

				// Tecla N → No
				if (key->scancode == sf::Keyboard::Scancode::N)
					return false;
			}
		}

		// Dibujar ventana
		v_monitor.ventana->clear(sf::Color::Black);
		v_monitor.dibujarElementos();
		v_monitor.ventana->display();
	}

	return false; // fallback si se cierra la ventana
}


void Disparo(Ventana& v_monitor, Ventana& v_tablero, Unidad& unidad, Ejercito& Ejer_enem)
{
	set<string> whitelist = { "Vehiculo", "Monstruo", "Pistola", "Asalto" };
	set<string> graylist = { "Vehiculo", "Monstruo" };
	TextBox* mensaje = v_monitor.TextBoxes[v_monitor.TextBoxes.size() - 1];
	bool puede_disparar = false;

	for (auto& m : unidad.miembros)
		if (m.rango.size() != 0)
		{
			puede_disparar = true;
			break;
		}
	if (!puede_disparar)
	{
		v_monitor.ventana->clear(sf::Color::Black);
		mensaje->setText(unidad.nombre + " no tiene armas para disparar");
		v_monitor.dibujarElementos();
		v_monitor.ventana->display();
		esperarConfirmacion(v_monitor);
		return;
	}

	set<string> keysu(unidad.claves.begin(), unidad.claves.end());
	set_intersection(keysu.begin(), keysu.end(), whitelist.begin(), whitelist.end(), std::inserter(keysu, keysu.begin()));
	for (auto& m : unidad.miembros)
		for (auto& a : m.rango)
		{
			set<string> keysa;
			for (auto& k : a.claves)
				keysa.insert(k.first);
			set_intersection(keysa.begin(), keysa.end(), whitelist.begin(), whitelist.end(), std::inserter(keysa, keysa.begin()));
			keysu.merge(keysa);
		}

	if (unidad.atk == 0)
	{
		v_monitor.ventana->clear(sf::Color::Black);
		mensaje->setText(unidad.nombre + "ya no puede disparar en este turno.");
	}

	bool asalto = false;
	if (unidad.atk == 1 && unidad.mov == 1 && (keysu.count("Asalto") == 1))
	{
		asalto = true;
		v_monitor.ventana->clear(sf::Color::Black);
		mensaje->setText(unidad.nombre + " solo puede disparar con armas de asalto en este turno");
		v_monitor.dibujarElementos();
		v_monitor.ventana->display();
		esperarConfirmacion(v_monitor);
	}
	else if (unidad.atk == 1 && !(keysu.count("Asalto") == 1))
	{
		v_monitor.ventana->clear(sf::Color::Black);
		mensaje->setText(unidad.nombre + " no puede disparar en este turno.");
		v_monitor.dibujarElementos();
		v_monitor.ventana->display();
		esperarConfirmacion(v_monitor);
		return;
	}

	set<string> keysu2;
	set_intersection(keysu.begin(), keysu.end(), whitelist.begin(), whitelist.end(), std::inserter(keysu2, keysu2.begin()));
	if (unidad.engaged && keysu2.size() == 0)
	{
		v_monitor.ventana->clear(sf::Color::Black);
		mensaje->setText(unidad.nombre + " no puede disparar, esta demasiado cerca de un enemigo.");
		v_monitor.dibujarElementos();
		v_monitor.ventana->display();
		esperarConfirmacion(v_monitor);
		return;
	}
	else
	{
		for (auto& m : unidad.miembros)
		{
			int indice = 0;
			while (true)
			{
				vector<bool> l_armas;
				for (auto& a : m.rango)
					l_armas.push_back(a.usado);
				if (allTrue(l_armas))
					break;

				int indice = Selec_Arma(v_tablero, unidad, m, true);
				if (!m.rango[indice].usado)
				{
					bool AsaltoInKeys;
					bool PrecisionInKeys;
					//Reutilizar el bucle para otras claves
					for (auto& par : m.rango[indice].claves)
					{
						if (par.first == "Asalto")
							AsaltoInKeys = true;
						else if (par.first == "Precision")
							PrecisionInKeys = true;
					}
					if (asalto && !AsaltoInKeys)
					{
						v_monitor.ventana->clear(sf::Color::Black);
						mensaje->setText("No puede disparar con " + m.rango[indice].nombre + " en este turno");
						v_monitor.dibujarElementos();
						v_monitor.ventana->display();
						esperarConfirmacion(v_monitor);
						continue;
					}
				}

				v_monitor.ventana->clear(sf::Color::Black);
				mensaje->setText("Elegiste: " + m.rango[indice].nombre);
				v_monitor.dibujarElementos();
				v_monitor.ventana->display();
				esperarConfirmacion(v_monitor);
				string accion = "Disparar";
				Unidad* blanco = Selec_Blanco(v_monitor, unidad, accion, Ejer_enem);
				if (blanco == nullptr)
				{
					m.rango[indice].usado = true;
					continue;
				}
				else
				{
					set <string> keysb;
					for (auto& k : blanco->claves)
						keysb.insert(k);
					set_intersection(keysb.begin(), keysb.end(), graylist.begin(), graylist.end(), std::inserter(keysb, keysb.begin()));
					if (blanco->engaged && keysb.empty())
					{
						v_monitor.ventana->clear(sf::Color::Black);
						mensaje->setText("No puede disparar a " + blanco->nombre + ", esta demasiado cerca de un aliado.");
						v_monitor.dibujarElementos();
						v_monitor.ventana->display();
						esperarConfirmacion(v_monitor);
						continue;
					}

					int dist = Visible(v_tablero, unidad, *blanco);
					if (dist > m.rango[indice].stats_map["Alcance"].get<int>() || dist == -1.f)
					{
						v_monitor.ventana->clear(sf::Color::Black);
						mensaje->setText("Objetivo fuera de alcance o no visible.");
						v_monitor.dibujarElementos();
						v_monitor.ventana->display();
						esperarConfirmacion(v_monitor);
						continue;
					}

					bool AgenteSolitarioInKeys = false;
					for (auto& c : blanco->claves)
					{
						if (c == "Agente Solitario")
							AgenteSolitarioInKeys = true;
					}
					if (blanco->lider != "" && AgenteSolitarioInKeys && dist >= 12)
					{
						v_monitor.ventana->clear(sf::Color::Black);
						mensaje->setText(blanco->nombre + " es un agente solitario y se ha escabullido.");
						v_monitor.dibujarElementos();
						v_monitor.ventana->display();
						esperarConfirmacion(v_monitor);
						continue;
					}
					else
					{
						string n = m.rango[indice].stats_map["No. de Ataques"].get<string>();
						int N;
						vector<int> N_dados;
						int tor = 0;

						if (m.rango[indice].claves.find("Area") != m.rango[indice].claves.end())
							if (blanco->engaged)
							{
								v_monitor.ventana->clear(sf::Color::Black);
								mensaje->setText(blanco->nombre + " esta demasiado cerca de una unidad aliada.");
								v_monitor.dibujarElementos();
								v_monitor.ventana->display();
								esperarConfirmacion(v_monitor);
								continue;
							}
							else
							{
								n = n + ("+" + to_string(blanco->miembros.size() / 5));
							}
						else if (m.rango[indice].claves.find("Fuego Rapido") != m.rango[indice].claves.end())
						{
							if (dist <= m.rango[indice].stats_map["Alcance"].get<int>() / 2)
							{
								v_monitor.ventana->clear(sf::Color::Black);
								mensaje->setText(unidad.nombre + " esta cerca de su objetivo y lanza ataques adicionales.");
								v_monitor.dibujarElementos();
								v_monitor.ventana->display();
								esperarConfirmacion(v_monitor);
								n = n + m.rango[indice].claves["Fuego Rapido"].get<string>();
							}
						}
						else if (m.rango[indice].claves.find("Torrente") != m.rango[indice].claves.end())
						{
							v_monitor.ventana->clear(sf::Color::Black);
							mensaje->setText(unidad.nombre + " es un arma de torrente e impacta directamente.");
							v_monitor.dibujarElementos();
							v_monitor.ventana->display();
							esperarConfirmacion(v_monitor);
							tor = 5;
						}

						if (n.find("D") == string::npos)
						{
							N = stoi(n);
							N_dados.clear();
						}
						else
						{
							N = 0;
							N_dados = AtkDmg_Rand(n);
						}

						vector <int> impact;
						int nAI = Repetida(m.rango[indice], unidad);

						if (nAI > 1)
						{
							string t = "Multiples miniaturas en " + unidad.nombre + " usan " +
								m.rango[indice].nombre + "\nDesea hacer una tirada rápida para dispararlas todas contra "
								+ blanco->nombre + "?";
							bool resp = Selec_SN(v_monitor, t);
							if (resp)
							{
								for (auto& mini : unidad.miembros)
								{
									for (auto& arma : mini.rango)
									{
										if (arma.nombre == m.rango[indice].nombre && !(arma.usado))
										{
											vector<int> tiradas;
											int Dx = tor ? tor : 6;
											tiradas = !(N_dados.empty()) ? AtkDmg_Rand(n) : Dados(N, Dx, false);
											impact.insert(impact.end(), tiradas.begin(), tiradas.end());
											arma.usado = true;
											if (mini.rango[indice].claves.find("Perfil") != m.rango[indice].claves.end())
												for (auto& ar : mini.rango)
													if (mini.rango[indice].claves.find("Perfil") != m.rango[indice].claves.end())
														ar.usado = true;
										}
										else
											continue;
									}
								}
							}
						}
						else
						{
							m.rango[indice].usado = true;
							if (m.rango[indice].claves.find("Perfil") != m.rango[indice].claves.end())
								for (auto& ar : m.rango)
									if (m.rango[indice].claves.find("Perfil") != m.rango[indice].claves.end())
										ar.usado = true;
							impact = !(N_dados.empty()) ? AtkDmg_Rand(n) : Dados(N, 6, false);
						}

						if (m.rango[indice].claves.find("Golpes Sostenidos") != m.rango[indice].claves.end())
						{
							string nGS = m.rango[indice].claves["Golpes Sostenidos"].get<string>();
							bool nGS_IsStr = (nGS.find("D") == string::npos);
							int nAD = 0;
							for (auto& d : impact)
								if (d == 6)
									nAD += nGS_IsStr ? stoi(nGS): AtkDmg_Rand(nGS, false);
							v_monitor.ventana->clear(sf::Color::Black);
							mensaje->setText(m.rango[indice].nombre + " hace Golpes Sostenidos: "+to_string(nAD));
							v_monitor.dibujarElementos();
							v_monitor.ventana->display();
							esperarConfirmacion(v_monitor);
							for (size_t i = 0; i< nAD; i++)
								impact.push_back(6);
						}

						else if (m.rango[indice].claves.find("Impactos Letales") != m.rango[indice].claves.end())
						{
							vector<int> seises;
							copy_if(impact.begin(), impact.end(), back_inserter(seises),[](int val) { return val == 6; });
							copy_if(impact.begin(), impact.end(), back_inserter(impact), [](int val) { return val != 6; });
							int m_ = m.rango[indice].claves["Impactos Letales"].get<int>();
							int dano = 0;
							for (auto& d : seises)
								dano += m_ ? Dados(1, 6);
							v_monitor.ventana->clear(sf::Color::Black);
							mensaje->setText(to_string(seises.size())+" impactos fueron letales");
							v_monitor.dibujarElementos();
							v_monitor.ventana->display();
							esperarConfirmacion(v_monitor);
						}
					}
				}
			}
		}
	}
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
	v_monitor.TextBoxes.push_back(msgBox);

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
			for (auto& circulo : unidad.circulos)
			{
				// Agregar las miniaturas al tablero
				v_tablero.Circulos.push_back(&circulo);
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
		while (const std::optional event = v_tablero.ventana->pollEvent())
		{
			if (event->is<sf::Event::Closed>())
				v_tablero.ventana->close();
		}
		while (const std::optional ev = v_tablero.ventana->pollEvent())
		{
			if (ev->is<sf::Event::Closed>())
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
