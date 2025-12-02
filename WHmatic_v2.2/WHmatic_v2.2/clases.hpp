#pragma once

#include <SFML/Graphics.hpp>
#include <SFML/Window.hpp>
#include <string>
#include <vector>
#include <map>
#include <algorithm>
#include <optional>
#include <iostream>

#include "json.hpp"
using json = nlohmann::json;
using namespace std;

//Clase base para los elementos de la interfaz
class Elemento
{
public:
    sf::Vector2f posicion;
    std::string Texto;
    sf::Texture textura;
    virtual ~Elemento() {};
    virtual string Type() {};
};

//Clase botón para la interfaz
class Boton : public Elemento
{
public:
    sf::Vector2f tamano;
    bool presionado = false;
    sf::RectangleShape rect;
    sf::Sprite* sprite = nullptr;
    sf::Font* font = nullptr;
    sf::Text* textoBoton;
    Boton(sf::Vector2f pos, sf::Vector2f tam, string texto)
    {
        this->presionado = false;
        this->posicion = pos;
        this->tamano = tam;
        this->Texto = texto;
        this->rect.setSize(this->tamano);
        this->rect.setPosition(this->posicion);
        this->font = new sf::Font();
        this->font->openFromFile("sprites/ARIAL.TTF");
        this->textoBoton->setString(texto);
        this->textoBoton->setCharacterSize(12);
        this->textoBoton->setFillColor(sf::Color::White);
        this->textoBoton->setPosition(pos);
    }
    Boton(sf::Vector2f pos, sf::Vector2f tam, sf::Texture tex)
    {
        this->presionado = false;
        this->posicion = pos;
        this->tamano = tam;
        this->sprite = new sf::Sprite(tex);
    }
    bool CheckClick(sf::Vector2i PosM) {
        if (PosM.x >= this->posicion.x && PosM.x <= this->posicion.x + this->tamano.x &&
            PosM.y >= this->posicion.y && PosM.y <= this->posicion.y + this->tamano.y)
        {
            this->presionado = true;
        }
        else
            this->presionado = false;
        return this->presionado;
    }
    virtual ~Boton() { delete this->sprite; }
    virtual string Type() override { return "Boton"; }
};

class TextBox : public Elemento
{
private:
    sf::RectangleShape box;
    sf::Text *text = nullptr;
    sf::Font* font = nullptr;

public:
    TextBox(
        const sf::Vector2f& size = {200.f, 50.f},
        const sf::Vector2f& position = {0.f, 0.f},
        const std::string& contenido = "TextBox"
    )
    {
        this->font = new sf::Font("sprites/ARIAL.TTF");
        this->text = new sf::Text(*font, contenido, 12);
        (*(this->text)).setFillColor(sf::Color(0, 255, 127)); // Spring Green

        // Configurar rectángulo
        this->box.setSize(size);
        this->box.setPosition(position);
        this->box.setFillColor(sf::Color::Black);
        this->box.setOutlineThickness(2.f);
        this->box.setOutlineColor(sf::Color::White);

        // Posicionar texto centrado
        centerText();
    }

    // Setter para texto
    void setText(const std::string& nuevo)
    {
        (*(this->text)).setString(nuevo);
        centerText();
    }

    // Setter de posición
    void setPosition(const sf::Vector2f& pos)
    {
        this->box.setPosition(pos);
        centerText();
    }

    // Ajustar tamaño
    void setSize(const sf::Vector2f& size)
    {
        this->box.setSize(size);
        centerText();
    }

	sf::RectangleShape* getBox() { return &(this->box); }

	sf::Text* getText() { return this->text; }

	string Type() override { return "TextBox"; }

private:
    // Centrar texto dentro del rectángulo
    void centerText()
    {
        sf::FloatRect boxBounds = this->box.getGlobalBounds();
        sf::FloatRect textBounds = (*(this->text)).getLocalBounds();

        (*(this->text)).setPosition({
            boxBounds.position.x + (boxBounds.size.x - textBounds.size.x) / 2.f - textBounds.position.x,
            boxBounds.position.y + (boxBounds.size.y - textBounds.size.y) / 2.f - textBounds.position.y
            }
        );
    }
};

//Clase Obstaculo para el tablero
class Obstaculo : public Elemento
{
public:
    sf::RectangleShape rect;
    Obstaculo(sf::Vector2f pos, sf::Vector2f tam)
    {
        this->rect.setPosition(pos);
        this->rect.setSize(tam);
        this->rect.setFillColor(sf::Color::Black);
    }

	virtual string Type() override { return "Obstaculo"; }

	sf::FloatRect getRect() { return this->rect.getGlobalBounds(); }

	string Type() override { return "Obstaculo"; }
};

class Ventana
{
public:
    sf::RenderWindow* ventana = nullptr;
    vector<Elemento*> elementos;
    sf::Vector2i PosMouse;
    Ventana(int Ancho, int Alto, string Nombre)
    {
        this->ventana = new sf::RenderWindow(sf::VideoMode({ Ancho, Alto }), Nombre);
        this->ventana->setFramerateLimit(60);
    }
    
    virtual ~Ventana() {
        delete this->ventana;
        for (size_t i = 0; i < this->elementos.size(); i++)
            delete this->elementos[i];
    }
    string Type() { return "Ventana"; }

    void dibujarElementos()
    {
        for (auto& e : this->elementos)
        {
            if (e->Type() == "Boton")
            {
                Boton* b = dynamic_cast<Boton*>(e);
                this->ventana->draw(b->rect);
                if (b->textoBoton)
                    this->ventana->draw(*(b->textoBoton));
                if (b->sprite)
                    this->ventana->draw(*(b->sprite));
            }
            else if (e->Type() == "TextBox")
            {
                TextBox* tb = dynamic_cast<TextBox*>(e);
                this->ventana->draw(*(tb->getBox()));
                this->ventana->draw(*(tb->getText()));
            }
            else if (e->Type() == "Obstaculo")
            {
                Obstaculo* o = dynamic_cast<Obstaculo*>(e);
                this->ventana->draw(o->rect);
            }
        }
    }
};

// Clase Arma (base)
class Arma {
public:
    std::string nombre;

    std::vector<std::string> tx = { "Alcance", "No. de Ataques",
          "Habilidad", "Fuerza", "Perforación", "Daño" };

    std::vector<json> stats_raw;

    std::map<std::string, json> stats_map;

    // claves puede contener valores null, arrays, enteros, etc.
    std::map<std::string, json> claves;

    bool usado;

    Arma()
    {
        this -> usado = false;
        for (size_t i = 0; i < tx.size(); i++)
            this->stats_map[tx[i]] = stats_raw[i]; //Llena el diccionario de stats
    }
    virtual ~Arma() = default;

    void Reboot()
    {
        this->usado = false;
    }

    void zip_stats()
    {
        // Combina tx + stats_raw para llenar stats_map de Arma
        for (size_t i = 0; i < tx.size(); i++)
        {
            if (i < this->stats_raw.size())
                this->stats_map[tx[i]] = this->stats_raw[i];
        }
    }
};

// Clase Individuo : Arma
class Individuo : public Arma {
public:
    // TX propia para Individuo (StatsTx). También la dejas vacía.
    vector<string> tx = { "Movimiento", "Resistencia", "Salvación",
           "Heridas", "Liderazgo", "Control de objetivo" };

    // Armas de rango y cuerpo a cuerpo (composición real)
    vector<Arma> rango;
    vector<Arma> mele;

    int dmg = 0;

    // En la semántica original, usado = true significa "vivo".
    Individuo():
        Arma()
    {
        this->usado = true;
    }

    string Recibir_Dano(Ventana& v_monitor, int& dano, map<string, json>& habs)
    {
        for (const auto& h : habs)
            if (h.first == "No hay dolor")
            {
                int nhd = h.second.get<int>();
                if (nhd > Dados(1, 6))
                {
                    this->dmg += dano;
                    return;
                }
                else
                    return "No hay dolor" + to_string(nhd) + "+ salvo " + to_string(dano) + " heridas";
            }
        this->dmg += dano;
        if (this->dmg >= this->stats_map["Heridas"].get<int>())
        {
            this->usado = false;
            // Por complejidad, se descarta Final Violento
			return this->nombre + "ha muerto";
        }
    }
};

// Clase Unidad
struct Unidad {
    string nombre;
    bool posLid = false;           // "Lider" en JSON (si viene)
    optional<std::string> lider; // nombre del líder (opcional)
    map<std::string, json> habilidades;
    vector<std::string> claves;
    int nm = 0; // Numero Miniaturas
	int Tamano_base; //Tamaño de la base de las miniaturas


    // Estados de juego
    bool engaged = false;
    bool shock = false;
    int mov = 0;
    int atk = 0;

    vector<Individuo> miembros;
	vector<sf::CircleShape> circulos; // Para representar la unidad en SFML

	Unidad() {};
    ~Unidad()
    {
        for (auto& c : this->circulos)
            delete &c;
    }


    // Método para eliminar minis muertas (usado == false)
    void eliminar_muertos() {
        miembros.erase(std::remove_if(miembros.begin(), miembros.end(),
            [](const Individuo& m) { return m.usado == false; }),
            miembros.end());
    }

    void crear_circulos()
    {
        for (int i = 0; i < this->miembros.size(); i++)
        {
            sf::CircleShape circulo;
            circulo.setRadius(this->Tamano_base / 2.0f);
            circulo.setFillColor(sf::Color::Green);
            circulo.setPosition({ 100.0f + i * (this->Tamano_base + 5.0f), 100.0f }); // Ejemplo de posición
            this->circulos.push_back(circulo);
		}
    }
};

// -------------------------
// Clase Ejercito
// -------------------------
class Ejercito {
public:
    std::string faccion;
    int nu = 0; // Numero Unidades
    int pc = 0;
    int pv = 0;

    std::vector<Unidad> unidades;

    Ejercito(){};

    void eliminar_unidades() {
        unidades.erase(std::remove_if(unidades.begin(), unidades.end(),
            [](const Unidad& u) { return u.miembros.empty(); }),
            unidades.end());
    }
};

// -------------------------
// Funciones from_json
// -------------------------
// Se definen fuera de las clases como funciones libres para que nlohmann::json
// las detecte automáticamente al usar get<T>() o get_to().
// A continuación se implementan para Arma, Individuo, Unidad y Ejercito.
// Comentario detallado incluido para from_json(const json&, Arma&)
// -------------------------
// 
// from_json para Arma
inline void from_json(const json& j, Arma& a) {
    //
    // Comentario detallado (explicación paso a paso)
    //
    // Propósito:
    //   - Cargar desde `j` los campos que pertenecen a una Arma
    //   - Guardar el vector original "Stats" en `stats_raw`.
    //   - Guardar "Claves" directamente en `claves`.
    //
    // Pasos:
    // 1) Nombre: si existe, asignarlo a a.nombre.
    // 2) Stats: si existe y es un array, copiar sus elementos en stats_raw.
    //    NO intentamos convertir a stats_map aquí porque `a.tx` está vacío
    //    por diseño; más adelante el usuario podrá combinar tx + stats_raw.
    // 3) Claves: si existe, iterar las entradas del objeto y volcarlas en
    //    el map<string,json> a.claves para mantener cualquier estructura.
    // 4) Usado: si existe un booleano "usado" en el JSON lo tomamos,
    //    si no existe dejamos el valor por defecto.
    //
    // Notas de diseño:
    //  - Usamos json como valor del map para mayor flexibilidad:
    //    claves pueden ser null, int, array, etc.

    // 1) Nombre
    if (j.contains("Nombre") && j["Nombre"].is_string()) {
        a.nombre = j["Nombre"].get<std::string>();
    }

    // 2) Stats -> stats_raw (guardamos todo tal cual)
    a.stats_raw.clear();
    if (j.contains("Stats") && j["Stats"].is_array()) {
        for (const auto& el : j["Stats"]) {
            a.stats_raw.push_back(el);
        }
    }

    // 3) Claves -> map<string,json>
    a.claves.clear();
    if (j.contains("Claves") && j["Claves"].is_object()) {
        for (auto it = j["Claves"].begin(); it != j["Claves"].end(); ++it) {
            // Copiamos el json tal cual (puede ser null, array, string, int...)
            a.claves[it.key()] = it.value();
        }
    }

    else if (j.contains("Usado")) {
        // Manejo de variantes de capitalización (por si el JSON usa 'Usado')
        if (j["Usado"].is_boolean()) a.usado = j["Usado"].get<bool>();
    }

    a.zip_stats();
}

// from_json para Individuo
inline void from_json(const json& j, Individuo& ind) {
    // Primero cargar la parte de Arma
    from_json(j, static_cast<Arma&>(ind));

    // rangos: puede ser "rangos" (array) en tu JSON
    ind.rango.clear();
    if (j.contains("rangos") && j["rangos"].is_array()) {
        for (const auto& r : j["rangos"]) {
            if (r.is_null()) continue;
            Arma a;
            from_json(r, a);
            ind.rango.push_back(std::move(a));
        }
    }

    // meles: puede ser "meles" (array) en tu JSON
    ind.mele.clear();
    if (j.contains("meles") && j["meles"].is_array()) {
        for (const auto& m : j["meles"]) {
            if (m.is_null()) continue;
            Arma a;
            from_json(m, a);
            ind.mele.push_back(std::move(a));
        }
    }

    ind.zip_stats();
}

// from_json para Unidad
inline void from_json(const json& j, Unidad& u) {
    if (j.contains("Nombre") && j["Nombre"].is_string())
        u.nombre = j["Nombre"].get<std::string>();

    if (j.contains("Lider")) {
        if (j["Lider"].is_boolean()) u.posLid = j["Lider"].get<bool>();
        else if (j["Lider"].is_string()) { u.posLid = true; u.lider = j["Lider"].get<std::string>(); }
    }

    u.habilidades.clear();
    if (j.contains("Habilidades") && j["Habilidades"].is_object()) {
        for (auto it = j["Habilidades"].begin(); it != j["Habilidades"].end(); ++it)
            u.habilidades[it.key()] = it.value();
    }

    u.claves.clear();
    if (j.contains("Claves") && j["Claves"].is_array())
        for (const auto& c : j["Claves"])
            if (c.is_string()) u.claves.push_back(c.get<std::string>());


    if (j.contains("Numero Miniaturas") && j["Numero Miniaturas"].is_number_integer())
        u.nm = j["Numero Miniaturas"].get<int>();

    if (j.contains("Base") && j["Base"].is_number_integer())
		u.Tamano_base = j["Base"].get<int>();

    // Miembros (vector de Individuo)
    u.miembros.clear();
    if (j.contains("minis") && j["minis"].is_array()) {
        for (const auto& m : j["minis"]) {
            if (m.is_null()) continue;
            Individuo ind;
            from_json(m, ind);
            u.miembros.push_back(std::move(ind));
        }
    }
}

// from_json para Ejercito
inline void from_json(const json& j, Ejercito& e) {
    if (j.contains("Faccion") && j["Faccion"].is_string())
        e.faccion = j["Faccion"].get<std::string>();

    if (j.contains("Numero Unidades") && j["Numero Unidades"].is_number_integer())
        e.nu = j["Numero Unidades"].get<int>();

    e.unidades.clear();
    if (j.contains("unidades") && j["unidades"].is_array()) {
        for (const auto& u : j["unidades"]) {
            if (u.is_null()) continue;
            Unidad uu;
            from_json(u, uu);
            e.unidades.push_back(std::move(uu));
        }
    }

    // También puede haber casos en que el JSON tenga "Unidades" u otra capitalización.
    if (e.unidades.empty() && j.contains("Unidades") && j["Unidades"].is_array()) {
        for (const auto& u : j["Unidades"]) {
            if (u.is_null()) continue;
            Unidad uu;
            from_json(u, uu);
            e.unidades.push_back(std::move(uu));
        }
    }
}
