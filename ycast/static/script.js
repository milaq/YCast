window.onload = function () {
    document.getElementById('idRequestSrc').value = 'recently';
    document.getElementById('idLanOrCountSelect').disabled = true;
    var requestSrc = document.getElementById('idRequestSrc').value;
    var param = document.getElementById('idLanOrCountSelect').value;
    requestStationList(requestSrc, param, false);

    requestStationList('', '', true);
    setBookmarkcategoryList();
}

function searchTree(element, id) {
    if (element.id === id) {
        return element;
    } else if (element.children != null) {
        var i;
        var result = null;
        for (i = 0; result == null && i < element.children.length; i++) {
            result = searchTree(element.children[i], id);
        }
        return result;
    }
    return null;
}


function createItem(name, icon, description) {

    var itemElem = document.createElement("div");
    itemElem.className = "item";

    var itemicon = document.createElement("div");
    itemicon.className = "itemicon";

    if (icon && icon.length > 0) {
        var itemiconimg = document.createElement("img");
        itemiconimg.src = icon;
        itemiconimg.className = "itemicon";
        itemicon.appendChild(itemiconimg);
    }

    var itemtext = document.createElement("div");
    itemtext.className = "itemtext";
    var h4text = document.createElement("h4");
    h4text.textContent = name;
    h4text.id = 'name'
    var desc = document.createElement("p");
    desc.textContent = description;
    desc.id = 'description';


    itemtext.appendChild(h4text);
    itemtext.appendChild(desc);

    itemElem.appendChild(itemicon);
    itemElem.appendChild(itemtext);

    return itemElem;
}


function requestStationList(category, param, isbookmarklist) {
    var url = 'api/stations?category=' + category;
    var id_listnode = "stationList";
    var countall = 0;
    if (isbookmarklist) {
        var url = 'api/bookmarks?category=' + category;
        var id_listnode = "bookmarkList";
    }
    if (param.length > 0) {
        if (category.indexOf('language') > -1) {
            url = url + '&language=' + param.toLowerCase();
        }
        if (category.indexOf('country') > -1) {
            url = url + '&country=' + param;
        }
    }
    var myRequest = new Request(url);
    var myOldList = document.getElementById(id_listnode);

    var myList = myOldList.cloneNode(false);
    // First Elemet is empty (workaround <ul> needs a <li> element)
    let listItemEmpty = document.createElement('li');
    listItemEmpty.appendChild(createItem('<<< loading >>>', '', ''));
    listItemEmpty.dataset.isemptyelement = 'true';
    listItemEmpty.hidden = false;
    myList.appendChild(listItemEmpty);
    myOldList.parentNode.replaceChild(myList, myOldList);

    fetch(myRequest)
        .then(response => response.json())
        .then(data => {
            for (const station of data) {
                countall = countall + 1;
                let listItem = document.createElement('li');
                listItem.appendChild(
                    createItem(station.name, station.icon, station.description)
                );
                listItem.dataset.json = JSON.stringify(station);
                if (isbookmarklist) {
                    listItem.dataset.search = (station.description);
                    listItem.onclick = function (event) {
                        deleteElement(event, listItem)
                    };
                } else {
                    listItem.dataset.search = (station.name + '#' + station.description).toUpperCase();
                    listItem.onclick = function (event) {
                        copyElementToBookmark(event, listItem)
                    };
                }
                listItem.dataset.category = station.description;
                listItem.dataset.isemptyelement = 'false';
                myList.appendChild(listItem);
                if (listItemEmpty) listItemEmpty.hidden = true;
            }
            if (listItemEmpty) {
                textElem = searchTree(listItemEmpty, 'name');
                if (textElem) textElem.textContent = '';
            }
            if (isbookmarklist) {
                setBookmarkcategoryList();
            } else {
                document.getElementById('stationcount').textContent = countall + '/' + countall;
            }

        })
        .catch(console.error);
}


function deleteElement(event, objElem) {
    if (objElem) {
        objElem.remove();
        refreshFilteredList(document.getElementById("bookmarkList"), document.getElementById('idcategory').value, true);
        setBookmarkcategoryList();
        saveBookmarks();
    }
}


function copyElementToBookmark(event, objElem) {
    if (objElem) {
        let myList = document.getElementById("bookmarkList")
        let listItem = document.createElement('li');
        let station = JSON.parse(objElem.dataset.json);
        let categoryElem = document.getElementById('idcategory');
        if (categoryElem.value.length == 0) categoryElem.value = 'Others'
        station.description = categoryElem.value;
        listItem.appendChild(
            createItem(station.name, station.icon, station.description)
        );
        listItem.dataset.json = JSON.stringify(station);
        listItem.dataset.search = station.description;
        listItem.dataset.category = station.description;
        listItem.dataset.isemptyelement = 'false';
        listItem.onclick = function (event) {
            deleteElement(event, listItem)
        };
        myList.appendChild(listItem);
        refreshFilteredList(document.getElementById("bookmarkList"), document.getElementById('idcategory').value, true);
        setBookmarkcategoryList();
        saveBookmarks();
    }
}

function refreshFilteredList(myListNode, filtertxt, chkEqual) {
    var isEmpty = true;
    var myListAr = Array.from(myListNode.childNodes);
    var emptyElement = null;
    var countall = 0;
    var countfiltered = 0;
    myListAr.forEach(function (listItem) {
        try {
            if (listItem.dataset.isemptyelement === 'true') {
                emptyElement = listItem;
            } else {
                countall = countall + 1;
                var bfound = true;
                if (filtertxt.length > 0) {
                    var searchval = listItem.dataset.search;
                    if (chkEqual) {
                        bfound = (searchval === filtertxt);
                    } else {
                        bfound = (searchval.indexOf(filtertxt) > -1);
                    }
                }
                if (bfound) {
                    countfiltered = countfiltered + 1;
                    listItem.hidden = false;
                    isEmpty = false;
                } else {
                    listItem.hidden = true;
                }
            }
        } catch (e) {
            console.error(listItem, e)
        }
    });
    if (emptyElement) emptyElement.hidden = !isEmpty;
    return countfiltered + '/' + countall;
}

function checkOptionElement(optionsElementList, value) {
    var optionList = Array.from(optionsElementList.childNodes);
    return optionList.find(function (optionElem) {
        return (optionElem.value === value)
    })
}

function onInputSelect(e, objElem) {
    switch (objElem.id) {
        case 'idRequestSrc':
            paramElem = document.getElementById('idLanOrCountSelect')
            param = paramElem.value
            category = objElem.value
            switch (category) {
                case 'language':
                    setParamlist();
                    try {
                        paramElem.fokus();
                    } catch (e) {};
                    return;
                case 'country':
                    setParamlist();
                    try {
                        paramElem.fokus();
                    } catch (e) {};
                    return;
                default:
                    paramElem.disabled = true;
                    break;
            }
            document.getElementById('stationcount').textContent = requestStationList(category, param);
            break;
        case 'idLanOrCountSelect':
            if (checkOptionElement(document.getElementById('listLangOrCountry'), document.getElementById('idLanOrCountSelect').value)) {
                document.getElementById('stationcount').textContent = requestStationList(
                    document.getElementById('idRequestSrc').value,
                    document.getElementById('idLanOrCountSelect').value);
            }
            break;

        case 'idcategory':
            refreshFilteredList(document.getElementById("bookmarkList"), document.getElementById('idcategory').value, true);
            break;

        case 'stationsearch':
            document.getElementById('stationcount').textContent =
                refreshFilteredList(document.getElementById('stationList'),
                    document.getElementById('stationsearch').value.toUpperCase(), false);
            break;
    }
}

function setBookmarkcategoryList() {
    var categoryList = [];
    var bookmarkList = Array.from(document.getElementById("bookmarkList").childNodes);
    bookmarkList.forEach(function (listItem) {
        try {
            if (listItem.dataset.isemptyelement === 'false') {
                var category = listItem.dataset.category;
                if (!categoryList.find(function (arElem) {
                        return (category === arElem);
                    })) {
                    categoryList.push(category);
                }
            }
        } catch (e) {
            console.error(listItem, e)
        }
    })
    if (categoryList.length > 0) {
        var myOldList = document.getElementById('categoryList');
        var myList = myOldList.cloneNode(false);
        myOldList.parentNode.replaceChild(myList, myOldList);

        for (const category of categoryList) {
            var option = document.createElement('option');
            option.value = category;
            myList.appendChild(option);
        }
    }
}


function setParamlist() {
    var category = document.getElementById('idRequestSrc').value
    var url = 'api/paramlist?category=' + category;
    document.getElementById('idLanOrCountSelect').value = '';
    var myRequest = new Request(url);
    var myOldList = document.getElementById('listLangOrCountry');
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
    document.getElementById('idLanOrCountSelect').disabled = false;
}

function keyUpEvent(e, objElem) {
    if (e instanceof KeyboardEvent) {
        if (e.code === 'Backspace') {
            objElem.value = '';
            switch (objElem.id) {
                case 'stationsearch':
                    document.getElementById('stationcount').textContent =
                        refreshFilteredList(document.getElementById('stationList'),
                            document.getElementById('stationsearch').value.toUpperCase(), false);
                    break;
                case 'idcategory':
                    refreshFilteredList(document.getElementById("bookmarkList"), document.getElementById('idcategory').value, true);
                    break;

                default:
                    break;
            }
            return;
        }
    }
    switch (objElem.id) {
        case 'idLanOrCountSelect':
            param = objElem.value;
            category = document.getElementById('idRequestSrc').value;
            if (e instanceof KeyboardEvent) {
                // it is a keyboard event!
                if (e.code == 'Enter') {
                    if (checkOptionElement(document.getElementById('listLangOrCountry'), param)) {
                        document.getElementById('stationcount').textContent = requestStationList(category, param);
                    }
                }
            } else if (e instanceof Event) {
                // one Element from selection is selected
                document.getElementById('stationcount').textContent = requestStationList(category, param);
            }
            break;
        case 'stationsearch':
            document.getElementById('stationcount').textContent =
                refreshFilteredList(document.getElementById('stationList'),
                    document.getElementById('stationsearch').value.toUpperCase(), false);
            break;
        case 'idcategory':
            refreshFilteredList(document.getElementById("bookmarkList"), document.getElementById('idcategory').value, true);
            break;
        default:
            break;
    }
}

function saveBookmarks() {
    var bookmarkJsonlist = []
    var bookmarkList = Array.from(document.getElementById("bookmarkList").childNodes);
    bookmarkList.forEach(function (listItem) {
        if (listItem.dataset.isemptyelement === 'false') {
            station = JSON.parse(listItem.dataset.json)
            bookmarkJsonlist.push(station)
        }
    })
    var data = JSON.stringify(bookmarkJsonlist)

    var xhr = new XMLHttpRequest();
    xhr.open("POST", 'api/bookmarks', true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var json = JSON.parse(xhr.responseText);
            console.log(json);
        }
    };
    xhr.send(data);
}
