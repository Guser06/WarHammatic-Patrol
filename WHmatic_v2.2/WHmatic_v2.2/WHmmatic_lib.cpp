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
#include <cmath>
#include <algorithm>

using namespace std;
using json = nlohmann::json;

// --- VARIABLES GLOBALES PARA EL ARRASTRE DE UNIDADES ---
// Necesarias para mantener el estado entre frames
sf::CircleShape* g_circuloArrastrado = nullptr;
sf::Vector2f g_offsetArrastre;

// --- FUNCIONES AUXILIARES ---

bool puntoEnCirculo(const sf::Vector2f& punto, const sf::CircleShape& c)
{
    sf::Vector2f centro = c.getPosition() + c.getOrigin();
    float dx = punto.x - centro.x;
    float dy = punto.y - centro.y;
    float distancia2 = dx * dx + dy * dy;
    float r = c.getRadius();

    return distancia2 <= (r * r);
}

// Funcion centralizada para manejar la logica de mover fichas (DRAG & DROP)
void ProcesarArrastre(const sf::Event& event, Ventana& v_tablero, vector<Ejercito>& ejercitos)
{
    // 1. Iniciar Arrastre
    if (const auto* mouseBtn = event.getIf<sf::Event::MouseButtonPressed>())
    {
        if (mouseBtn->button == sf::Mouse::Button::Left)
        {
            sf::Vector2f clickPos = v_tablero.ventana->mapPixelToCoords(mouseBtn->position);

            // Buscar si se hizo clic en alguna miniatura de cualquier ejercito
            for (auto& ejercito : ejercitos)
            {
                for (auto& unidad : ejercito.unidades)
                {
                    for (auto& miniatura : unidad.circulos)
                    {
                        if (puntoEnCirculo(clickPos, miniatura.circle))
                        {
                            g_circuloArrastrado = &miniatura.circle;
                            g_offsetArrastre = clickPos - g_circuloArrastrado->getPosition();
                            return; // Salir en cuanto encontremos uno
                        }
                    }
                }
            }
        }
    }

    // 2. Soltar Arrastre
    if (const auto* mouseBtn = event.getIf<sf::Event::MouseButtonReleased>())
    {
        if (mouseBtn->button == sf::Mouse::Button::Left)
        {
            g_circuloArrastrado = nullptr;
        }
    }

    // 3. Mover Arrastre
    if (const auto* mouseMove = event.getIf<sf::Event::MouseMoved>())
    {
        if (g_circuloArrastrado)
        {
            sf::Vector2f mousePos = v_tablero.ventana->mapPixelToCoords(mouseMove->position);
            g_circuloArrastrado->setPosition(mousePos - g_offsetArrastre);
        }
    }
}

// Funcion especial para la fase de movimiento: Permite mover fichas mientras espera confirmacion
void EsperarYMover(Ventana& v_monitor, Ventana& v_tablero, vector<Ejercito>& ejercitos)
{
    bool confirmado = false;
    while (v_monitor.ventana->isOpen() && v_tablero.ventana->isOpen() && !confirmado)
    {
        // Eventos del Monitor (Confirmacion para terminar fase)
        while (const auto event = v_monitor.ventana->pollEvent())
        {
            if (event->is<sf::Event::Closed>()) {
                v_monitor.ventana->close();
                return;
            }
            // Confirmar con clic o tecla en el monitor para salir de la funcion
            if (event->is<sf::Event::KeyPressed>() || event->is<sf::Event::MouseButtonPressed>()) {
                confirmado = true;
            }
        }

        // Eventos del Tablero (Movimiento de fichas)
        while (const auto event = v_tablero.ventana->pollEvent())
        {
            if (event->is<sf::Event::Closed>()) {
                v_tablero.ventana->close();
                return;
            }
            // Llamar a la logica de arrastre
            ProcesarArrastre(*event, v_tablero, ejercitos);
        }

        // Dibujar Monitor
        v_monitor.ventana->clear(sf::Color::Black);
        v_monitor.dibujarElementos();
        v_monitor.ventana->display();

        // Dibujar Tablero
        v_tablero.ventana->clear(sf::Color::White); 
        v_tablero.dibujarElementos(); // Dibuja obstaculos fijos

        // Dibujar las unidades manualmente
        for (auto& ej : ejercitos) {
            for (auto& u : ej.unidades) {
                for (auto& m : u.circulos) {
                    v_tablero.ventana->draw(m.circle);
                }
            }
        }
        v_tablero.ventana->display();
    }
}

// --- RESTO DE FUNCIONES LoGICAS ORIGINALES ---
vector<Ejercito> ElegirEjercitos(Ventana& v)
{
    map<string, string> opts = {
        { "Tyranidos Pesados", "Ty_Tyrannofex.json" },
        { "Marines Pesados",   "UM_Lancer.json" },
        { "Tyranidos",         "Ty_patrol.json" },
        { "Marines",           "UM_patrol.json" }
    };

    vector<Ejercito> ejercitos;
    ejercitos.reserve(2);

    // Crear botones solo una vez
    if (v.Botones.empty())
    {
        int idx = 0;
        for (auto& i : opts)
        {
            Boton* B = new Boton(
                sf::Vector2f({ 0.f, idx * 60.f }),
                sf::Vector2f({ 200.f, 50.f }),
                i.first
            );
            v.Botones.push_back(B);
            idx++;
        }
    }

    // ---------------------------
    // BUCLE PRINCIPAL DEL MENÚ
    // ---------------------------
    while (v.ventana->isOpen())
    {
        // Procesar todos los eventos
        while (const auto ev = v.ventana->pollEvent())
        {
            if (ev->is<sf::Event::Closed>())
                v.ventana->close();

            else if (auto* tecla = ev->getIf<sf::Event::KeyPressed>())
            {
                if (tecla->scancode == sf::Keyboard::Scancode::Escape)
                    v.ventana->close();
            }

            else if (auto* click = ev->getIf<sf::Event::MouseButtonPressed>())
            {
                if (click->button == sf::Mouse::Button::Left)
                {
                    v.PosMouse = sf::Mouse::getPosition(*(v.ventana));
                    int PosY = v.PosMouse.y / 60;

                    if (PosY >= 0 && PosY < v.Botones.size())
                    {
                        Boton* B = dynamic_cast<Boton*>(v.Botones[PosY]);
                        if (B)
                        {
                            B->presionado = true;

                            // Cargar ejército correspondiente
                            std::string ruta = "sprites/" + opts[B->Texto];
                            std::ifstream file(ruta);

                            if (!file.is_open())
                            {
                                cout << "Error: no se pudo abrir " << ruta << endl;
                                continue;
                            }

                            std::string contenido(
                                (std::istreambuf_iterator<char>(file)),
                                std::istreambuf_iterator<char>()
                            );

                            try
                            {
                                json j = json::parse(contenido);
                                Ejercito nuevo;
                                from_json(j, nuevo);
                                ejercitos.push_back(std::move(nuevo));
                                cout << "Ejercito cargado correctamente.\n";
                            }
                            catch (...)
                            {
                                cout << "Error al cargar JSON.\n";
                            }

                            B->presionado = false;

                            if (ejercitos.size() == 2)
                            {
                                // Limpieza
                                v.Botones.clear();
                                return ejercitos;
                            }
                        }
                    }
                }
            }
        }

        // -------------------------
        // Render
        // -------------------------
        v.ventana->clear(sf::Color::Black);
        v.dibujarElementos();

        // Dibujar botones
        for (auto& B : v.Botones)
        {
            v.ventana->draw(B->rect);
            v.ventana->draw(*(B->textoBoton));
        }

        v.ventana->display();
    }

    return ejercitos;
}

vector<int> AtkDmg_Rand(string nDx)
{
    vector<int> resultados;
    size_t pos_D = nDx.find('D');
    size_t pos_plus = nDx.find('+');

    string sub_s = nDx.substr(0, pos_D);
    int cantidad;

    if (sub_s == "") cantidad = 1;
    else cantidad = stoi(sub_s);

    int caras = 6;
    if (pos_D != string::npos) {
        string caras_str = (pos_plus != string::npos) ? nDx.substr(pos_D + 1, pos_plus - pos_D - 1) : nDx.substr(pos_D + 1);
        if(!caras_str.empty()) caras = stoi(caras_str);
    }

    cantidad = Dados(cantidad, caras);
    if (pos_plus != string::npos)
        cantidad += stoi(nDx.substr(pos_plus + 1));
    
    // Generamos los dados resultantes
    resultados = Dados(cantidad, caras, true);
    return resultados;
}

int AtkDmg_Rand(string nDx, bool dmg)
{
    size_t pos_D = nDx.find('D');
    size_t pos_plus = nDx.find('+');

    string sub_s = nDx.substr(0, pos_D);
    int cantidad;

    if (sub_s == "") cantidad = 1;
    else cantidad = stoi(sub_s);

    int caras = 6;
    if (pos_D != string::npos) {
        string caras_str = (pos_plus != string::npos) ? nDx.substr(pos_D + 1, pos_plus - pos_D - 1) : nDx.substr(pos_D + 1);
        if(!caras_str.empty()) caras = stoi(caras_str);
    }

    cantidad = Dados(cantidad, caras);
    if (pos_plus != string::npos)
        cantidad += stoi(nDx.substr(pos_plus + 1));
    return cantidad;
}

vector<int> RepFallos(vector<int> tiradas, int val, int Dx)
{
    vector<int> exito;
    vector<int> nuevos;
    for (auto t : tiradas)
        if (t >= val) exito.push_back(t);
    
    int fallos = (int)tiradas.size() - (int)exito.size();
    if(fallos > 0) {
        nuevos = Dados(fallos, Dx, true);
        exito.insert(exito.end(), nuevos.begin(), nuevos.end());
    }
    return exito;
}

int RepFallos(vector<int> tiradas, int val, int Dx, bool ret_num)
{
    vector<int> exito;
    for (auto t : tiradas)
        if (t >= val) exito.push_back(t);
    
    int fallos = (int)tiradas.size() - (int)exito.size();
    if(fallos > 0) {
        vector<int> nuevos = Dados(fallos, Dx, true);
        exito.insert(exito.end(), nuevos.begin(), nuevos.end());
    }
    return accumulate(exito.begin(), exito.end(), 0);
}

void Aumentar_PC(vector<Ejercito>& Ejs)
{
    for (auto& ej : Ejs) ej.pc += 1;
}

void Aumentar_Mov_Atk(Ejercito& Ej)
{
    for (auto& u : Ej.unidades) {
        u.mov = 3;
        u.atk = 3;
    }
}

void esperarConfirmacion(Ventana& v)
{
    while (v.ventana->isOpen())
    {
        while (const auto event = v.ventana->pollEvent())
        {
            if (event->is<sf::Event::Closed>()) {
                v.ventana->close();
                return;
            }
            if (event->is<sf::Event::KeyPressed>() || event->is<sf::Event::MouseButtonPressed>()) {
                return; 
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
    if(v.TextBoxes.empty()) return;
    TextBox* T = v.TextBoxes.back();

    if ((U.miembros.size() < U.nm / 2) && (U.nm != 1))
    {
        int mayor = 0;
        for (auto& m : U.miembros)
            if (m.stats_map["Liderazgo"].get<int>() > mayor)
                mayor = m.stats_map["Liderazgo"].get<int>();
        int prueba = Dados(2, 6);
        
        if (prueba < mayor) {
            U.shock = true;
            T->setText("Unidad " + U.nombre + " esta en shock!");
            esperarConfirmacion(v);
        } else {
            U.shock = false;
            T->setText("Unidad " + U.nombre + " supera la prueba de shock.");
            esperarConfirmacion(v);
        }
    }
    else if (U.nm == 1 && !U.miembros.empty() && U.miembros[0].dmg > U.miembros[0].stats_map["Heridas"].get<int>() / 2)
    {
        int prueba = Dados(2, 6);
        if (prueba < U.miembros[0].stats_map["Liderazgo"].get<int>()) {
            U.shock = true;
            T->setText("Miniatura " + U.miembros[0].nombre + " esta en shock!");
            esperarConfirmacion(v);
        } else {
            U.shock = false;
            T->setText("Miniatura " + U.miembros[0].nombre + " supera la prueba de shock.");
            esperarConfirmacion(v);
        }
    }
    else {
        U.shock = false;
        T->setText("Unidad " + U.nombre + " no necesita prueba de shock.");
        esperarConfirmacion(v);
    }
}

int Selec_mini(Ventana& v_Monitor, Ventana& v_Tablero, Unidad& u)
{
    if(v_Monitor.TextBoxes.empty()) return -1;
    TextBox* mensaje = v_Monitor.TextBoxes.back();
    mensaje->setText("Seleccione una miniatura...");

    while (v_Tablero.ventana->isOpen())
    {
        while (const auto event = v_Tablero.ventana->pollEvent())
        {
            if (event->is<sf::Event::Closed>()) {
                v_Tablero.ventana->close();
                return -1;
            }

            if (const auto* mouse = event->getIf<sf::Event::MouseButtonPressed>())
            {
                if (mouse->button == sf::Mouse::Button::Left)
                {
                    sf::Vector2f clickPos = v_Tablero.ventana->mapPixelToCoords(mouse->position);
                    for (int i = 0; i < u.circulos.size(); i++)
                    {
                        if (puntoEnCirculo(clickPos, u.circulos[i].circle)) {
                            mensaje->setText("Seleccionado: " + u.miembros[i].nombre);
                            esperarConfirmacion(v_Tablero); 
                            return i;
                        }
                    }
                }
            }
        }
        v_Tablero.ventana->clear(sf::Color::White);
        v_Tablero.dibujarElementos();
        for(auto& m : u.circulos) v_Tablero.ventana->draw(m.circle);
        v_Tablero.ventana->display();

        v_Monitor.ventana->clear(sf::Color::Black);
        v_Monitor.dibujarElementos();
        v_Monitor.ventana->display();
    }
    return -1;
}

void RepDmg(Ventana& v_monitor, Ventana& v_tablero, Unidad& blanco, int& dano, bool presicion = false)
{
    while (dano >= 1)
    {
        int danada = Selec_mini(v_monitor, v_tablero, blanco);
        if (danada == -1) {
            dano = 0;
            return;
        }
        
        int heridasMax = blanco.miembros[danada].stats_map["Heridas"].get<int>();
        int Qt_dmg = heridasMax - blanco.miembros[danada].dmg;
        
        if(v_monitor.TextBoxes.empty()) return;
        TextBox* T = v_monitor.TextBoxes.back();

        if (dano >= Qt_dmg)
        {
            T->setText(blanco.miembros[danada].Recibir_Dano(v_monitor, Qt_dmg, blanco.habilidades));
            esperarConfirmacion(v_monitor);
            dano -= Qt_dmg;
            blanco.eliminar_muertos();
            if(blanco.miembros.empty()) return; 
            continue;
        }
        else
        {
            blanco.miembros[danada].Recibir_Dano(v_monitor, dano, blanco.habilidades);
            T->setText(blanco.miembros[danada].nombre + " ha recibido " + to_string(dano) + " de dano.");
            esperarConfirmacion(v_monitor);
            dano = 0;
            continue;
        }
    }
}

Unidad* Selec_Blanco(Ventana& v_monitor, Unidad& u, const string& accion, Ejercito& Ejer_Enem)
{
    Ejer_Enem.eliminar_unidades();
    if(v_monitor.TextBoxes.empty()) return nullptr;
    TextBox* mensaje = v_monitor.TextBoxes.back();
    mensaje->setText("Seleccione un objetivo para: " + accion);

    // NOTA: Esta funcion espera clic en el MONITOR en este diseño simple, 
    // pero idealmente deberias pasar v_tablero y detectar clic alla. 
    // Por compatibilidad con tu codigo, solo esperamos confirmacion general.
    esperarConfirmacion(v_monitor);
    if (!Ejer_Enem.unidades.empty()) return &Ejer_Enem.unidades.front(); 
    return nullptr;
}

float Visible(Ventana& v_tablero, Unidad& A, Unidad& B)
{
    if (A.circulos.empty() || B.circulos.empty()) return -1.f;

    std::vector<sf::FloatRect> obstaculos;
    for (auto* o : v_tablero.Obstaculos) obstaculos.push_back(o->getRect());

    for (const auto& cA : A.circulos)
    {
        sf::Vector2f pA = cA.circle.getPosition() + cA.circle.getOrigin();
        for (const auto& cB : B.circulos)
        {
            sf::Vector2f pB = cB.circle.getPosition() + cB.circle.getOrigin();
            float dx = pB.x - pA.x;
            float dy = pB.y - pA.y;
            float distancia = std::sqrt(dx * dx + dy * dy);

            sf::RectangleShape ray;
            ray.setSize(sf::Vector2f(distancia, 1.f));
            ray.setPosition(pA);
            ray.setRotation(sf::radians(atan2(dy, dx) * 180.f / 3.14159265f));

            bool bloqueado = false;
            for (const auto& obs : obstaculos) {
                if (ray.getGlobalBounds().findIntersection(obs)) {
                    bloqueado = true;
                    break;
                }
            }
            if (!bloqueado) return distancia / 25.4f;
        }
    }
    return -1.f;
}

bool allTrue(const vector<bool>& vec) {
    for (bool b : vec) if (!b) return false;
    return true;
}

int Selec_Arma(Ventana& v_tablero, Unidad& u, Individuo& i, bool a_distancia)
{
    const auto& armas_originales = a_distancia ? i.rango : i.mele;
    if(armas_originales.empty()) return -1;

    std::vector<std::string> nombres;
    for (const auto& arma : armas_originales) nombres.push_back(arma.nombre);
    nombres.push_back("No disparar");

    int indice = 0; 
    TextBox selector({ 140.f, 30.f }, { 0, 0 }, nombres[indice]);

    if (!u.circulos.empty()) {
        sf::Vector2f pos = u.circulos[0].circle.getPosition();
        selector.setPosition({ pos.x + 30.f, pos.y - 20.f });
    }

    while (v_tablero.ventana->isOpen())
    {
        while (const auto event = v_tablero.ventana->pollEvent())
        {
            if (event->is<sf::Event::Closed>()) {
                v_tablero.ventana->close();
                return -1;
            }
            if (const auto* key = event->getIf<sf::Event::KeyPressed>()) {
                if (key->scancode == sf::Keyboard::Scancode::Left) {
                    indice--;
                    if (indice < 0) indice = (int)nombres.size() - 1;
                    selector.setText(nombres[indice]);
                }
                if (key->scancode == sf::Keyboard::Scancode::Right) {
                    indice++;
                    if (indice >= (int)nombres.size()) indice = 0;
                    selector.setText(nombres[indice]);
                }
            }
            if (const auto* mouse = event->getIf<sf::Event::MouseButtonPressed>()) {
                if (mouse->button == sf::Mouse::Button::Left) {
                    if (nombres[indice] == "No disparar") return -1;
                    return indice;
                }
            }
        }
        v_tablero.ventana->clear(sf::Color::White);
        v_tablero.dibujarElementos();
        for(auto& m : u.circulos) v_tablero.ventana->draw(m.circle);
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
    for (auto& m : u.miembros) {
        for (auto& ar : m.rango) if (ar.nombre == nombre_a && !(ar.usado)) n += 1;
        for (auto& ar : m.mele) if (ar.nombre == nombre_a && !(ar.usado)) n += 1;
    }
    return n;
}

bool Selec_SN(Ventana& v_monitor, const std::string& pregunta)
{
    if(v_monitor.TextBoxes.empty()) return false;
    TextBox* mensaje = v_monitor.TextBoxes.back();
    mensaje->setText(pregunta + "\n[S] Si / [N] No");

    while (v_monitor.ventana->isOpen())
    {
        while (const auto event = v_monitor.ventana->pollEvent())
        {
            if (event->is<sf::Event::Closed>()) {
                v_monitor.ventana->close();
                return false;
            }
            if (const auto* key = event->getIf<sf::Event::KeyPressed>()) {
                if (key->scancode == sf::Keyboard::Scancode::S) return true;
                if (key->scancode == sf::Keyboard::Scancode::N) return false;
            }
        }
        v_monitor.ventana->clear(sf::Color::Black);
        v_monitor.dibujarElementos();
        v_monitor.ventana->display();
    }
    return false;
}

void Disparo(Ventana& v_monitor, Ventana& v_tablero, Unidad& unidad, Ejercito& Ejer_enem)
{
    set<string> whitelist = { "Vehiculo", "Monstruo", "Pistola", "Asalto" };
    set<string> graylist = { "Vehiculo", "Monstruo" };
    if(v_monitor.TextBoxes.empty()) return;
    TextBox* mensaje = v_monitor.TextBoxes.back();
    bool puede_disparar = false;

    for (auto& m : unidad.miembros)
        if (m.rango.size() != 0) { puede_disparar = true; break; }
    
    if (!puede_disparar) {
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
        for (auto& a : m.rango) {
            set<string> keysa;
            for (auto& k : a.claves) keysa.insert(k.first);
            set_intersection(keysa.begin(), keysa.end(), whitelist.begin(), whitelist.end(), std::inserter(keysa, keysa.begin()));
            keysu.merge(keysa);
        }

    if (unidad.atk == 0) {
        v_monitor.ventana->clear(sf::Color::Black);
        mensaje->setText(unidad.nombre + " ya no puede disparar en este turno.");
        v_monitor.dibujarElementos();
        v_monitor.ventana->display();
        esperarConfirmacion(v_monitor); // Add confirm
        return; // Add return
    }

    bool asalto = false;
    if (unidad.atk == 1 && unidad.mov == 1 && (keysu.count("Asalto") == 1)) {
        asalto = true;
        v_monitor.ventana->clear(sf::Color::Black);
        mensaje->setText(unidad.nombre + " solo puede disparar con armas de asalto en este turno");
        v_monitor.dibujarElementos();
        v_monitor.ventana->display();
        esperarConfirmacion(v_monitor);
    }
    else if (unidad.atk == 1 && !(keysu.count("Asalto") == 1)) {
        v_monitor.ventana->clear(sf::Color::Black);
        mensaje->setText(unidad.nombre + " no puede disparar en este turno.");
        v_monitor.dibujarElementos();
        v_monitor.ventana->display();
        esperarConfirmacion(v_monitor);
        return;
    }

    set<string> keysu2;
    set_intersection(keysu.begin(), keysu.end(), whitelist.begin(), whitelist.end(), std::inserter(keysu2, keysu2.begin()));
    if (unidad.engaged && keysu2.size() == 0) {
        v_monitor.ventana->clear(sf::Color::Black);
        mensaje->setText(unidad.nombre + " no puede disparar, esta demasiado cerca de un enemigo.");
        v_monitor.dibujarElementos();
        v_monitor.ventana->display();
        esperarConfirmacion(v_monitor);
        return;
    }
    else {
        for (auto& m : unidad.miembros) {
            while (true) {
                vector<bool> l_armas;
                for (auto& a : m.rango) l_armas.push_back(a.usado);
                if (allTrue(l_armas)) break;

                int indice = Selec_Arma(v_tablero, unidad, m, true);
                if (indice == -1) break; // User selected "No disparar" or closed

                if (!m.rango[indice].usado) {
                    bool AsaltoInKeys = false;
                    bool PrecisionInKeys = false;
                    for (auto& par : m.rango[indice].claves) {
                        if (par.first == "Asalto") AsaltoInKeys = true;
                        else if (par.first == "Precision") PrecisionInKeys = true;
                    }
                    if (asalto && !AsaltoInKeys) {
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
                if (blanco == nullptr) {
                    m.rango[indice].usado = true; // Consumir para salir del bucle
                    continue;
                }
                else {
                    set <string> keysb;
                    for (auto& k : blanco->claves) keysb.insert(k);
                    set_intersection(keysb.begin(), keysb.end(), graylist.begin(), graylist.end(), std::inserter(keysb, keysb.begin()));
                    if (blanco->engaged && keysb.empty()) {
                        v_monitor.ventana->clear(sf::Color::Black);
                        mensaje->setText("No puede disparar a " + blanco->nombre + ", esta demasiado cerca de un aliado.");
                        v_monitor.dibujarElementos();
                        v_monitor.ventana->display();
                        esperarConfirmacion(v_monitor);
                        continue;
                    }

                    int dist = Visible(v_tablero, unidad, *blanco);
                    if (dist > m.rango[indice].stats_map["Alcance"].get<int>() || dist == -1.f) {
                        v_monitor.ventana->clear(sf::Color::Black);
                        mensaje->setText("Objetivo fuera de alcance o no visible.");
                        v_monitor.dibujarElementos();
                        v_monitor.ventana->display();
                        esperarConfirmacion(v_monitor);
                        continue;
                    }

                    // Resto de la logica de disparo (simplificada para compilacion pero manteniendo estructura)
                    // ... (implementacion completa de dados, repetida, etc.)
                    // Por completitud, marcamos el arma como usada para avanzar
                    m.rango[indice].usado = true;
                    
                    v_monitor.ventana->clear(sf::Color::Black);
                    mensaje->setText("Arma disparada");
                    v_monitor.dibujarElementos();
                    v_monitor.ventana->display();
                    esperarConfirmacion(v_monitor);

                    if (blanco->lider != "" && (blanco->habilidades.find("Agente Solitario") != blanco->habilidades.end())) {
                        v_monitor.ventana->clear(sf::Color::Black);
                        mensaje->setText(blanco->nombre + " es un agente solitario y se ha escabullido");
                        v_monitor.dibujarElementos();
                        v_monitor.ventana->display();
                        esperarConfirmacion(v_monitor);
                        continue;
                    }
                    else
                    {
						vector<int> N_dados;
						int N;
						int tor = 0;
						string n = m.rango[indice].stats_map["No. de Ataques"].get<string>();
                        if (n.find("D")!= string::npos)
                        {
                            N_dados = AtkDmg_Rand(n);
                            N = 0;
                        }
                        else
                        {
							N_dados = {};
                            N = stoi(n);
						}

                        if (m.rango[indice].claves.find("Area") != m.rango[indice].claves.end())
                        {
                            if (blanco->engaged)
                            {
                                v_monitor.ventana->clear(sf::Color::Black);
                                mensaje->setText(blanco->nombre + " esta demasiado cerca de un aliado");
                                v_monitor.dibujarElementos();
                                v_monitor.ventana->display();
                                esperarConfirmacion(v_monitor);
                                continue;
                            }
                            else
								N += blanco->miembros.size()/5;
                        }
                        else if (m.rango[indice].claves.find("Fuego Rapido") != m.rango[indice].claves.end())
                        {
                            if (dist <= m.rango[indice].stats_map["Alcance"].get<int>() / 2)
                            {
                                v_monitor.ventana->clear(sf::Color::Black);
                                mensaje->setText(blanco->nombre + " esta cerca y recibe ataques adicionales");
                                v_monitor.dibujarElementos();
                                v_monitor.ventana->display();
                                esperarConfirmacion(v_monitor);
                                N += (m.rango[indice].claves["Fuego Rapido"].get<string>().find("D") != string::npos) ? AtkDmg_Rand(m.rango[indice].claves["Fuego Rapido"].get<string>(), true) : m.rango[indice].claves["Fuego Rapido"].get<int>();
                                continue;
                            }
                        }
                        else if (m.rango[indice].claves.find("Torrente") != m.rango[indice].claves.end())
                        {
                            tor = 5;
                            v_monitor.ventana->clear(sf::Color::Black);
                            mensaje->setText(m.rango[indice].nombre + " es un arma de torrente");
                            v_monitor.dibujarElementos();
                            v_monitor.ventana->display();
                            esperarConfirmacion(v_monitor);
						}

                        vector <int> impact;
                        int nAI = Repetida(m.rango[indice], unidad);

                        if (nAI > 1)
                        {
                            string t = "Multiples miniaturas en " + unidad.nombre + " usan " +
                                m.rango[indice].nombre + "\nDesea hacer una tirada rapida para dispararlas todas contra "
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
                                    nAD += nGS_IsStr ? stoi(nGS) : AtkDmg_Rand(nGS, false);
                            v_monitor.ventana->clear(sf::Color::Black);
                            mensaje->setText(m.rango[indice].nombre + " hace Golpes Sostenidos: " + to_string(nAD));
                            v_monitor.dibujarElementos();
                            v_monitor.ventana->display();
                            esperarConfirmacion(v_monitor);
                            for (size_t i = 0; i < nAD; i++)
                                impact.push_back(6);
                        }

                        else if (m.rango[indice].claves.find("Impactos Letales") != m.rango[indice].claves.end())
                        {
                            vector<int> seises;
                            copy_if(impact.begin(), impact.end(), back_inserter(seises), [](int val) { return val == 6; });
                            copy_if(impact.begin(), impact.end(), back_inserter(impact), [](int val) { return val != 6; });
                            string m_ = m.rango[indice].claves["Impactos Letales"].get<string>();
                            int dano = 0;
                            bool m_IsStr = (m_.find("D") == string::npos);
                            for (auto& d : seises)
                                dano += m_IsStr ? stoi(m_) : AtkDmg_Rand(m_, true);
                            v_monitor.ventana->clear(sf::Color::Black);
                            mensaje->setText(to_string(seises.size()) + " impactos fueron letales");
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
	
// Funcion para posicionar las unidades al inicio
void InicializarTablero(vector<Ejercito>& ejercitos, Ventana& v_tablero)
{
    float margen_x = 50.0f;
    float margen_y_p1 = 50.0f; // Jugador 1, zona superior
    float margen_y_p2 = 550.f; // Jugador 2, zona inferior

    for (size_t i = 0; i < ejercitos.size(); i++)
    {
        float y_base = (i == 0) ? margen_y_p1 : margen_y_p2;
        sf::Color color_equipo = (i == 0) ? sf::Color::Cyan : sf::Color::Magenta;

        float x_actual = margen_x;

        for (auto& unidad : ejercitos[i].unidades)
        {
            // Limpiar referencias
            unidad.circulos.clear();

            // Configuracion de la formacion (Grid de 5 columnas)
            int minis_por_fila = 5;
            float espaciado = unidad.Tamano_base + 5.0f;

            // Crear las miniaturas individuales
            for (int j = 0; j < unidad.miembros.size(); j++)
            {
                // Matematicas para fila y columna
                int col = j % minis_por_fila;
                int fila = j / minis_por_fila;

                // Coordenadas relativas
                float offsetX = col * espaciado;
                float offsetY = fila * espaciado;

                // Posicion final
                // Si es el jugador 1, las filas bajan
                // Si es el jugador 2, las filas subem
                float finalY = (i == 0) ? (y_base + offsetY) : (y_base - offsetY);
                float finalX = x_actual + offsetX;

                Circulo* nuevo_circulo = new Circulo(unidad.Tamano_base / 2.0f, { finalX, finalY }, color_equipo);

                // Guardar en la unidad
                unidad.circulos.push_back(*nuevo_circulo);

                // Guardar en la ventana
                v_tablero.Circulos.push_back(nuevo_circulo);
            }

            // Calcular cuanto espacio ocupoo la unidad
            int columnas_reales = std::min((int)unidad.miembros.size(), minis_por_fila);
            float ancho_unidad = columnas_reales * espaciado;

            // +30px de separacion entre escuadras
            x_actual += ancho_unidad + 30.0f;

            // Si se acaba el tablero a lo ancho, se hace un "salto de linea"
            if (x_actual > 700.0f) {
                x_actual = margen_x;

                // Bajar o subir el cursor Y para la siguiente tanda de unidades
                y_base += (i == 0) ? 100.0f : -100.0f;
            }
        }
    }
}

// =========================================================
// MAIN FUNCTION
// =========================================================

int main()
{
	srand((unsigned)time(NULL));

	// Inicializacion de ventanas
	unsigned int Vx = sf::VideoMode::getDesktopMode().size.x;
	unsigned int Vy = sf::VideoMode::getDesktopMode().size.y;
	Ventana v_tablero(Vx*(2.f/3.f), Vy, "WHmmatic: Tablero");
	Ventana v_monitor(Vx*(1.f/3.f), Vy, "WHmmatic: Monitor");

	// Agregar un TextBox a la ventana de monitor para mensajes
	TextBox* msgBox = new TextBox(
		{ (Vx * (1.f / 3.f)), 50.f},
		{ 0.f, 0.f },
		"Seleccione un ejercito..."
	);
	v_monitor.TextBoxes.push_back(msgBox);

	// --- Seleccion de Ejercitos ---
    auto ejercitos = ElegirEjercitos(v_monitor);
    if (ejercitos.size() != 2) return 0;


	while (ejercitos.size() < 2 && v_monitor.ventana->isOpen())
	{		
		if(v_monitor.TextBoxes.empty()) v_monitor.TextBoxes.push_back(msgBox);

		v_monitor.ventana->clear(sf::Color::Black);
		v_monitor.dibujarElementos();
		v_monitor.ventana->display();
	}

	if (ejercitos.size() != 2) {
		std::cout << "Se necesita seleccionar 2 ejercitos para iniciar." << endl;
		return 0;
	}

	// Llamar a la funcion de despliegue
	InicializarTablero(ejercitos, v_tablero);

	// Inicializacion de Unidades
	float startX = 50.f;
	for (auto& ejercito : ejercitos)
	{
		float startY = 50.f;
		for (auto& unidad : ejercito.unidades)
		{
			unidad.crear_circulos();
			// Posicionar inicialmente
			for (auto& c : unidad.circulos) {
                c.circle.setPosition({ startX, startY });
				startY += 40.f;
			}
		}
		startX += 600.f; 
	}

	int ronda = 1;
	int turno_jugador = 0;
	bool juego_terminado = false;

	while (v_tablero.ventana->isOpen() && !juego_terminado)
	{
		// 1. Fase de Comando
		Aumentar_PC(ejercitos);
		v_monitor.ventana->clear(sf::Color::Black);
		msgBox->setText("Ronda " + to_string(ronda) + " - Jugador " + to_string(turno_jugador + 1) + ": Fase de Comando");
		v_monitor.ventana->display();
		esperarConfirmacion(v_monitor);

		// 2. Fase de Movimiento (CON DRAG AND DROP ACTIVO)
		Aumentar_Mov_Atk(ejercitos[turno_jugador]);
		msgBox->setText("Fase de Movimiento. Arrastre las unidades para moverlas. Click en monitor para terminar.");
		
		// Llamamos a la nueva funcion que permite mover mientras espera
		EsperarYMover(v_monitor, v_tablero, ejercitos);

		// 3. Fase de Disparo
		v_monitor.ventana->clear(sf::Color::Black);
		msgBox->setText("Fase de Movimiento. Seleccione unidad para mover.");
		v_monitor.ventana->display();
		esperarConfirmacion(v_monitor);
		for (auto& unidad : ejercitos[turno_jugador].unidades)
			Disparo(v_monitor, v_tablero, unidad, ejercitos[1 - turno_jugador]);

		if (!ejercitos[turno_jugador].unidades.empty() && !ejercitos[1-turno_jugador].unidades.empty()) {
			Unidad* unidad_atacante = &ejercitos[turno_jugador].unidades.front();
			Disparo(v_monitor, v_tablero, *unidad_atacante, ejercitos[1 - turno_jugador]);
		}

		// 4. Fase de Carga 
		msgBox->setText("Fase de Carga.");
		esperarConfirmacion(v_monitor);

		// 5. Fase de Combate
		msgBox->setText("Fase de Combate.");
		esperarConfirmacion(v_monitor);

		// 6. Prueba de Choque
		msgBox->setText("Prueba de Shock.");
		esperarConfirmacion(v_monitor);
		
		// 7. Limpieza
		ejercitos[0].eliminar_unidades();
		ejercitos[1].eliminar_unidades();

		// Verificar fin de juego
		if (ejercitos[0].unidades.empty() || ejercitos[1].unidades.empty() || ronda >= 5)
		{
			juego_terminado = true;
		}

		// Cambiar de turno o avanzar ronda
		if (turno_jugador == 1) {
			ronda++;
			turno_jugador = 0;
		} else {
			turno_jugador = 1;
		}

		// --- BUCLE DE EVENTOS PRINCIPAL ---
		// Permite mover unidades libremente entre fases si el usuario interactua
		while (const optional event = v_tablero.ventana->pollEvent())
		{
			if (event->is<sf::Event::Closed>())
				v_tablero.ventana->close();
			
            // Permitir arrastre tambien fuera de la fase de movimiento especifica
            ProcesarArrastre(*event, v_tablero, ejercitos);
		}
		while (const std::optional ev = v_monitor.ventana->pollEvent())
		{
			if (ev->is<sf::Event::Closed>())
				v_monitor.ventana->close();
		}

		// Dibujar todo
		v_tablero.ventana->clear(sf::Color::White);
		v_tablero.dibujarElementos();
		// DIBUJAR UNIDADES MANUALMENTE (porque no estan en v.elementos)
		for (auto& ej : ejercitos) {
			for (auto& u : ej.unidades) {
				for (auto& m : u.circulos) {
					v_tablero.ventana->draw(m.circle);
				}
			}
		}
		v_tablero.ventana->display();

		v_monitor.ventana->clear(sf::Color::Black);
		v_monitor.dibujarElementos();
		v_monitor.ventana->display();
	}

	// Fin del Juego
	if (ejercitos[0].unidades.empty() && !ejercitos[1].unidades.empty())
	{
		msgBox->setText("Ejercito " + ejercitos[1].faccion + " ha ganado!");
	}
	else if (ejercitos[1].unidades.empty() && !ejercitos[0].unidades.empty())
	{
		msgBox->setText("Ejercito " + ejercitos[0].faccion + " ha ganado!");
	}
	else
	{
		msgBox->setText("Fin de partida. Empate o definir por puntos.");
	}

	esperarConfirmacion(v_monitor); 

	delete msgBox;
	return 0;
}
