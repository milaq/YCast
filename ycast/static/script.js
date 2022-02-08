window.onload = function () {
    category = document.getElementById('id_category').value;
    param = document.getElementById('id_param').value;
    requestStationList(category, param) 
    
}

function initSearch() {
    var stationsearch = document.getElementById('stationsearch');
    stationsearch.value = '';
    stationsearch.onkeyup = function () {
        var filter = stationsearch.value.toUpperCase();
        var lis = document.getElementsByTagName('li');
        for (var i = 0; i < lis.length; i++) {
            var searchval = lis[i].dataset.search;
            if (searchval.indexOf(filter) > -1)
                lis[i].style.display = 'flex';
            else
                lis[i].style.display = 'none';
        }
    }
}

function createItem(name, icon, description) {

    var itemElem = document.createElement("div");
    itemElem.className = "item";

    var itemicon = document.createElement("div");
    itemicon.className = "itemicon";
    var itemiconimg = document.createElement("img");
    itemiconimg.src = icon;
    itemiconimg.className = "itemicon";

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

function requestStationList(category, param) {
    var url = 'api/stations?category=' + category;

    if (category.indexOf('language') > -1) {
        url = url + '&language=' + param.toLowerCase();
    }
    if (category.indexOf('country') > -1) {
        url = url + '&country=' + param;
    }
    var myRequest = new Request(url);
    var myOldList = document.getElementById("stationList");

    var myList = myOldList.cloneNode(false);
    myOldList.parentNode.replaceChild(myList, myOldList);

    fetch(myRequest)
        .then(response => response.json())
        .then(data => {
            for (const station of data) {
                let listItem = document.createElement('li');
                listItem.appendChild(
                    createItem(station.name, station.icon, station.description)
                );
                listItem.dataset.json = JSON.stringify(station);
                listItem.dataset.search = (station.name + '#' + station.description).toUpperCase();
                myList.appendChild(listItem);
            }
        })
        .catch(console.error);
    initSearch();
}

function onInputSelect(e, objElem) {

    if (objElem.id == 'id_category') {
        paramElem = document.getElementById('id_param')
        param = paramElem.value
        category = objElem.value
        switch (category) {
            case 'language':
                setParamlist();
                try {paramElem.fokus();} catch(e) {};
                return;
            case 'country':
                setParamlist();
                try {paramElem.fokus();} catch(e) {};
                return;
            default:
                paramElem.disabled = true;
                break;
        }
        requestStationList(category, param);
    }
}

function setParamlist() {
    var category = document.getElementById('id_category').value
    var url = 'api/paramlist?category=' + category;
    document.getElementById('id_param').value = '';
    var myRequest = new Request(url);
    var myOldList = document.getElementById('paramlist');

    var myList = myOldList.cloneNode(false);
    myOldList.parentNode.replaceChild(myList, myOldList);


    fetch(myRequest)
        .then(response => response.json())
        .then(data => {
            for (const param of data) {
                var option = document.createElement('option');
                option.value = param.name;
                myList.appendChild(option);
            }
        })
        .catch(console.error);
    document.getElementById('id_param').disabled = false;
}

function keyUpEvent(e, objElem) {
    switch (objElem.id) {
        case 'id_param':
            param = objElem.value;
            category = document.getElementById('id_category').value;
            if (e instanceof KeyboardEvent) {
                // it is a keyboard event!
                if (e.code == 'Enter') {
                    requestStationList(category, param);
                } else if (e.code == 'Backspace')
                    this.value = '';
            } else if (e instanceof Event) {
                // one Element from selection is selected
                requestStationList(category, param);
            }
            break;
        default:
            break;
    }
}
