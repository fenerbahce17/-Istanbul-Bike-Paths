from flask import Flask, render_template, request, jsonify
import folium
import json
import os
import osmnx as ox
import networkx as nx
from folium.plugins import Draw

app = Flask(__name__)

@app.route('/')
def index():
    bike_paths_data = None  

    try:
        geojson_path = os.path.join(os.getcwd(), 'data/istanbul_bisiklet_yollari.geojson')

        if os.path.exists(geojson_path):
            with open(geojson_path, encoding='utf-8') as f:
                bike_paths_data = json.load(f)
        else:
            print(f"GeoJSON dosyası bulunamadı: {geojson_path}")

    except Exception as e:
        print(f"GeoJSON dosyası okunurken hata oluştu: {e}")

    if bike_paths_data is None:
        bike_paths_data = {}

    # Harita nesnesini oluştur
    m = folium.Map(location=[41.015137, 28.979530], zoom_start=12)
    folium.GeoJson(bike_paths_data, name='Bisiklet Yolları').add_to(m)
    
    # Nokta koyma aracını ekle
    Draw(export=True).add_to(m)

    map_html = m._repr_html_()
    return render_template('index.html', map_html=map_html)
@app.route('/calculate_route', methods=['POST'])
def calculate_route():
    try:
        print("İstek alındı!")  # Debug için
        print("Gelen JSON:", request.data)  # Gelen veriyi göster

        data = request.get_json(force=True)
        print("Çözümlenmiş JSON:", data)  # JSON doğru okunuyor mu?

        if not data or "start" not in data or "end" not in data:
            print("Eksik veri!")  # Eksikse uyarı ver
            return jsonify({"error": "Başlangıç ve bitiş noktaları eksik!"}), 400

        start = tuple(data["start"])
        end = tuple(data["end"])
        print(f"Başlangıç: {start}, Bitiş: {end}")  # Noktaları kontrol et

        # Rota hesaplama
        G = ox.graph_from_place("Istanbul, Turkey", network_type="bike")
        orig_node = ox.nearest_nodes(G, start[1], start[0])
        dest_node = ox.nearest_nodes(G, end[1], end[0])
        route = nx.shortest_path(G, orig_node, dest_node, weight="length")
        route_coords = [(G.nodes[n]['y'], G.nodes[n]['x']) for n in route]

        print("Rota başarıyla hesaplandı!")  # Rota tamamlandıysa yazdır
        return jsonify({"route": route_coords})

    except Exception as e:
        print("Hata oluştu:", str(e))  # Hata mesajı
        return jsonify({"error": f"Rota hesaplanırken hata oluştu: {str(e)}"}), 500



if __name__ == '__main__':
    app.run(debug=True)