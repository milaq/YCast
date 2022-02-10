
window.onload = function () {
    category = document.getElementById('id_category').value;
    param = document.getElementById('id_param').value;
    requestStationList(category, param);
    requestStationList('', '', true);
}


function initSearchStation() {
    var stationsearch = document.getElementById('stationsearch');
    stationsearch.value = '';
    stationsearch.onkeyup = function (event) {
        if(event.code == 'Backspace')
            stationsearch.value = '';
        var filter = stationsearch.value.toUpperCase();
        document.getElementById('stationcount').textContent = refreshFilteredList(
                document.getElementById('stationList'), filter, false );
    }
}


function initSearchBookmark() {
    bookmarksearch = document.getElementById('idCategory');
    bookmarksearch.value = '';
    bookmarksearch.onkeyup = function (event) {
        if(event.code == 'Backspace')
            document.getElementById('idCategory').value = '';
        refreshFilteredList(document.getElementById("bookmarkList"), document.getElementById('idCategory').value, true);
    }
}


function createItem(name, icon, description) {

    var itemElem = document.createElement("div");
    itemElem.className = "item";

    var itemicon = document.createElement("div");
    itemicon.className = "itemicon";

    if (icon.length > 0){
        var itemiconimg = document.createElement("img");
        itemiconimg.src = icon;
        itemiconimg.className = "itemicon";
        itemicon.appendChild(itemiconimg);
    }

    var itemtext = document.createElement("div");
    itemtext.className = "itemtext";
    var h4text = document.createElement("h4");
    h4text.textContent = name;
    var desc = document.createElement("p");
    desc.textContent = description;


    itemtext.appendChild(h4text);
    itemtext.appendChild(desc);

    itemElem.appendChild(itemicon);
    itemElem.appendChild(itemtext);

    return itemElem;
}


function requestStationList(category, param, isbookmarklist = false) {
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
    listItemEmpty.appendChild(createItem('','', ''));
    listItemEmpty.dataset.isemptyelement = true;
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
                if(isbookmarklist){
                    listItem.dataset.search = (station.description);
                    listItem.onclick = function (event) {deleteElement(event,listItem)};
                } else {
                    listItem.dataset.search = (station.name + '#' + station.description).toUpperCase();
                    listItem.onclick = function (event) {copyElementToBookmark(event,listItem)};
                }
                listItem.dataset.category = station.description;
                listItem.dataset.emptyelement = false;
                myList.appendChild(listItem);
                if (listItemEmpty) listItemEmpty.hidden = true;
            }
            if(isbookmarklist) {
                setBookmarkCategoryList();
            } else {
                document.getElementById('stationcount').textContent = countall + '/' + countall;
            }

         })
        .catch(console.error);
    initSearchStation();
    initSearchBookmark();
}


function deleteElement(event, objElem){
    if(objElem) {
        objElem.remove();
        refreshFilteredList(document.getElementById("bookmarkList"), document.getElementById('idCategory').value, true);
        setBookmarkCategoryList()
    }
}


function copyElementToBookmark(event, objElem){
    if(objElem) {
        let myList = document.getElementById("bookmarkList")
        let listItem = document.createElement('li');
        let station = JSON.parse(objElem.dataset.json);
        let bookmarksearch = document.getElementById('idCategory');
        if(bookmarksearch.value.length == 0) bookmarksearch.value = 'Others'
        station.description = bookmarksearch.value;
        listItem.appendChild(
            createItem(station.name , station.icon, station.description)
        );
        listItem.dataset.json = JSON.stringify(station);
        listItem.dataset.search = station.description;
        listItem.dataset.category =  station.description;
        listItem.dataset.emptyelement = false;
        listItem.onclick = function (event) {deleteElement(event,listItem)};
        myList.appendChild(listItem);
        refreshFilteredList(document.getElementById("bookmarkList"), document.getElementById('idCategory').value, true);
        setBookmarkCategoryList();
    }
}

function refreshFilteredList(myListNode, filtertxt, chkEqual = false){
    var isEmpty = true;
    var myListAr = Array.from(myListNode.childNodes);
    var emptyElement = null;
    var countall = 0;
    var countfiltered = 0;
    myListAr.forEach(function (listItem) {
        try {
            if (listItem.dataset.isemptyelement){
                emptyElement = listItem;
            } else {
                countall = countall+1;
                let bfound = true;
                if (filtertxt.length > 0) {
                    var searchval = listItem.dataset.search;
                    if(chkEqual) {
                        bfound = (searchval === filtertxt);
                    } else {
                        bfound = (searchval.indexOf(filtertxt) > -1);
                    }
                }
                if(bfound) {
                    countfiltered = countfiltered + 1;
                    listItem.hidden =  false;
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
    return countfiltered + '/' +countall;
}

function onInputSelect(e, objElem) {

    switch(objElem.id){
        case 'id_category':
            paramElem = document.getElementById('id_param')
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
        case 'id_param':
            document.getElementById('stationcount').textContent = requestStationList(
                document.getElementById('id_category').value,
                document.getElementById('id_param').value);
            break;

        case 'idCategory':
            refreshFilteredList(document.getElementById("bookmarkList"), document.getElementById('idCategory').value, true);
            break;

        case 'stationsearch':
            document.getElementById('stationcount').textContent =
            refreshFilteredList(document.getElementById('stationList'),
            document.getElementById('stationsearch').value.toUpperCase(), false );
            break;
   }
}

function setBookmarkCategoryList() {
    var categoryList = [];
    var bookmarkList = Array.from(document.getElementById("bookmarkList").childNodes);
    bookmarkList.forEach(function (listItem) {
        try {
            if(!listItem.dataset.isemptyelement) {
                var category = listItem.dataset.category;
                if (!categoryList.find(function(arElem) { return (category == arElem);})) {
                    categoryList.push(category);
                }
            }
        } catch (e) {
            console.error(listItem, e)
        }
    })
    if (categoryList.length >0) {
        var myOldList = document.getElementById('categorylist');
        var myList = myOldList.cloneNode(false);
        myOldList.parentNode.replaceChild(myList, myOldList);
    
        for (const categ of categoryList) {
            var option = document.createElement('option');
            option.value = categ;
            myList.appendChild(option);
        }
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
                    document.getElementById('stationcount').textContent = requestStationList(category, param);
                } else if (e.code == 'Backspace')
                    this.value = '';
            } else if (e instanceof Event) {
                // one Element from selection is selected
                document.getElementById('stationcount').textContent = requestStationList(category, param);
            }
            break;
        default:
            break;
    }
}

function saveBookmarks(){
    var bookmarkJsonlist=[]
    var bookmarkList = Array.from(document.getElementById("bookmarkList").childNodes);
    bookmarkList.forEach(function (listItem) {
        if(!listItem.dataset.isemptyelement) {
            station = JSON.parse(listItem.dataset.json)
            bookmarkJsonlist.push( station )
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