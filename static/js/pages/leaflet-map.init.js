var osmUrl = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
var osmAttr = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors';

var mymap = L.map("leaflet-map").setView([51.505, -0.09], 13);
L.tileLayer(osmUrl, { maxZoom: 18, attribution: osmAttr }).addTo(mymap);

var markermap = L.map("leaflet-map-marker").setView([51.505, -0.09], 13);
L.tileLayer(osmUrl, { maxZoom: 18, attribution: osmAttr }).addTo(markermap);
L.marker([51.5, -0.09]).addTo(markermap);
L.circle([51.508, -0.11], { color: "#34c38f", fillColor: "#34c38f", fillOpacity: 0.5, radius: 500 }).addTo(markermap);
L.polygon([[51.509, -0.08], [51.503, -0.06], [51.51, -0.047]], { color: "#556ee6", fillColor: "#556ee6" }).addTo(markermap);

var popupmap = L.map("leaflet-map-popup").setView([51.505, -0.09], 13);
L.tileLayer(osmUrl, { maxZoom: 18, attribution: osmAttr }).addTo(popupmap);
L.marker([51.5, -0.09]).addTo(popupmap).bindPopup("<b>Hello world!</b><br />I am a popup.").openPopup();

var customiconsmap = L.map("leaflet-map-custom-icons").setView([51.5, -0.09], 13);
L.tileLayer(osmUrl, { maxZoom: 18, attribution: osmAttr }).addTo(customiconsmap);

var LeafIcon = L.Icon.extend({
  options: {
    iconSize: [45, 95],
    iconAnchor: [22, 94],
    popupAnchor: [-3, -76]
  }
});

var greenIcon = new LeafIcon({ iconUrl: "../../../static/images/logo-sm.svg" });
L.marker([51.5, -0.09], { icon: greenIcon }).addTo(customiconsmap);

var interactivemap = L.map("leaflet-map-interactive-map").setView([37.8, -96], 4);
L.tileLayer(osmUrl, { maxZoom: 18, attribution: osmAttr }).addTo(interactivemap);

function getColor(e) {
  return e > 1000 ? "#435fe3" :
         e > 500 ? "#556ee6" :
         e > 200 ? "#677de9" :
         e > 100 ? "#798ceb" :
         e > 50 ? "#8a9cee" :
         e > 20 ? "#9cabf0" :
         e > 10 ? "#aebaf3" : "#c0c9f6";
}

function style(e) {
  return {
    weight: 2,
    opacity: 1,
    color: "white",
    dashArray: "3",
    fillOpacity: 0.7,
    fillColor: getColor(e.properties.density)
  };
}

if (typeof statesData !== "undefined") {
  L.geoJson(statesData, { style: style }).addTo(interactivemap);
}

var cities = L.layerGroup();
L.marker([39.61, -105.02]).bindPopup("This is Littleton, CO.").addTo(cities);
L.marker([39.74, -104.99]).bindPopup("This is Denver, CO.").addTo(cities);
L.marker([39.73, -104.8]).bindPopup("This is Aurora, CO.").addTo(cities);
L.marker([39.77, -105.23]).bindPopup("This is Golden, CO.").addTo(cities);

var streets = L.tileLayer(osmUrl, { maxZoom: 18, attribution: osmAttr });
var grayscale = L.tileLayer(osmUrl, { maxZoom: 18, attribution: osmAttr });

var layergroupcontrolmap = L.map("leaflet-map-group-control", {
  center: [39.73, -104.99],
  zoom: 10,
  layers: [streets, cities]
});

var baseLayers = {
  Streets: streets,
  Grayscale: grayscale
};

var overlays = {
  Cities: cities
};

L.control.layers(baseLayers, overlays).addTo(layergroupcontrolmap);