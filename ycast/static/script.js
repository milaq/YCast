function createItem(name, icon, description) {
    
    var itemElem = document.createElement("div");
    itemElem.className = "item";

    var itemicon = document.createElement("div");
    itemicon.className = "itemicon";
    var itemiconimg = document.createElement("img");
    itemiconimg.src = icon;

    var itemtext = document.createElement("div");
    itemtext.className = "itemtext";
    var h4text = document.createElement("h4"); 
    h4text.textContent = name;
    var desc = document.createElement("p");
    desc.textContent = description;
    
    itemicon.appendChild(itemiconimg);
    
    itemtext.appendChild(h4text);
    itemtext.appendChild(desc);

    itemElem.appendChild(itemicon);
    itemElem.appendChild(itemtext);

    return itemElem;
}

function stationsAddItem() {
    var listElemet = document.createElement("li");
    listElemet.className = "item";
    listElemet.appendChild(createItem(" Halle self created","http://www.klassikradio.de/_nuxt/icons/icon_64.a00w80w0000.png","classic, poppi"));

    document.getElementById("stationList").appendChild(listElemet);
}

