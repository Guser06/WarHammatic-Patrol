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
        this->textoBoton->setString("Reintentar?");
        this->textoBoton->setCharacterSize(24);
        this->textoBoton->setFillColor(sf::Color::Black);
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
};


// -------------------------
// Clase Arma (base)
// -------------------------
class Arma {
    std::string nombre;

    // TX: vector de strings que actuarán como 'headers' (ArmaTx).
    // Lo dejas vacío y lo llenarás después externamente.
    std::vector<std::string> tx = { "Alcance", "No. de Ataques",
          "Habilidad", "Fuerza", "Perforación", "Daño" };

    // stats_raw guarda directamente el array "Stats" del JSON en orden.
    // Útil para luego "zipear" con tx cuando tx esté disponible.
    std::vector<json> stats_raw;

    // stats_map puede rellenarse después combinando tx con stats_raw.
    // Usamos json para permitir int, string, null o estructuras complejas.
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
};

// -------------------------
// Clase Individuo : Arma
// -------------------------
class Individuo : public Arma, public Elemento {
    // TX propia para Individuo (StatsTx). También la dejas vacía.
    std::vector<std::string> tx = { "Movimiento", "Resistencia", "Salvación",
           "Heridas", "Liderazgo", "Control de objetivo" };

    // Armas de rango y cuerpo a cuerpo (composición real)
    std::vector<Arma> rango;
    std::vector<Arma> mele;

    int dmg = 0;

    // En la semántica original, usado = true significa "vivo".
    Individuo():
        Arma()
    {
        this->usado = true;
    }


};

// -------------------------
// Clase Unidad
// -------------------------
struct Unidad {
    std::string nombre;
    bool posLid = false;           // "Lider" en JSON (si viene)
    std::optional<std::string> lider; // nombre del líder (opcional)
    std::map<std::string, json> habilidades;
    std::vector<std::string> claves;
    int nm = 0; // Numero Miniaturas

    // Estados de juego
    bool engaged = false;
    bool shock = false;
    int mov = 0;
    int atk = 0;

    std::vector<Individuo> miembros;

    // Método para eliminar minis muertas (usado == false)
    void eliminar_muertos() {
        miembros.erase(std::remove_if(miembros.begin(), miembros.end(),
            [](const Individuo& m) { return m.usado == false; }),
            miembros.end());
    }
};

// -------------------------
// Clase Ejercito
// -------------------------
struct Ejercito {
    std::string faccion;
    int nu = 0; // Numero Unidades
    int pc = 0;
    int pv = 0;

    std::vector<Unidad> unidades;

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

// -------------------------
// from_json para Arma
// -------------------------
inline void from_json(const json& j, Arma& a) {
    //
    // Comentario detallado (explicación paso a paso)
    //
    // Propósito:
    //   - Cargar desde `j` los campos que pertenecen a una Arma,
    //     sin suponer que exista un "tx" (vector de nombres de estadística).
    //   - Guardar el vector original "Stats" en `stats_raw`.
    //   - Guardar "Claves" directamente en `claves`.
    //   - Dejar `tx` vacío (el usuario lo completará después); si `tx`
    //     ya estuviera no sobrescribimos pero intentamos no convertir
    //     automáticamente `stats_raw` en `stats_map` a menos que tx esté presente.
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
    //  - stats_raw mantiene el orden; la conversión a stats_map debe
    //    realizarse llamando a una función auxiliar una vez que `tx` esté definido.
    //

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

    // 4) Usado (opcional en JSON)
    if (j.contains("usado")) {
        // Si el JSON define 'usado' y es booleano, lo tomamos.
        if (j["usado"].is_boolean()) a.usado = j["usado"].get<bool>();
    }
    else if (j.contains("Usado")) {
        // Manejo de variantes de capitalización (por si el JSON usa 'Usado')
        if (j["Usado"].is_boolean()) a.usado = j["Usado"].get<bool>();
    }

    //
    // Observación sobre la conversión stats_raw -> stats_map:
    // Si en algún momento se rellenan `a.tx` con la lista de nombres de cada estadística:
    //
    //    // ejemplo (pseudocódigo):
    //    if (a.tx.size() == a.stats_raw.size()) {
    //        for (size_t i=0; i<a.tx.size(); ++i)
    //            a.stats_map[a.tx[i]] = a.stats_raw[i];
    //    }
    //
    // Dejo esa responsabilidad para tu código porque dijiste que llenarás `tx`
    // externamente (por ejemplo en inicialización global o al cargar reglas).
    //
}

// -------------------------
// from_json para Individuo
// -------------------------
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
}

// -------------------------
// from_json para Unidad
// -------------------------
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
    if (j.contains("Claves") && j["Claves"].is_array()) {
        for (const auto& c : j["Claves"]) {
            if (c.is_string()) u.claves.push_back(c.get<std::string>());
        }
    }

    if (j.contains("Numero Miniaturas") && j["Numero Miniaturas"].is_number_integer())
        u.nm = j["Numero Miniaturas"].get<int>();

    // Estados (opcional)
    if (j.contains("engaged") && j["engaged"].is_boolean()) u.engaged = j["engaged"].get<bool>();
    if (j.contains("shock") && j["shock"].is_boolean()) u.shock = j["shock"].get<bool>();

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

// -------------------------
// from_json para Ejercito
// -------------------------
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
