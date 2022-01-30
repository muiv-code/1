const backendAddr = "http://localhost:9099/"
let partTypes = [];
fillSelectOptions();
addOnsubmitAction();

// Загрузка с бэкенда моделей конфигурации.

function fillSelectOptions() {
    httpGet(backendAddr + "get-options", function (text) {
        // Проходимся в каллбэке по всему массиву, применяем опции формат массива: {"cpu": {"core i6", "core i7"}}
        JSON.parse(text, addSelectOption);
    });
}

function httpGet(addr, callback) {
    // Создаем объект для http-запроса.
    let http = new XMLHttpRequest();
    // Создаем функцию-триггер, которая сработает после загрузки ответа от бэкенда.
    http.onreadystatechange = function () {
        if (http.readyState == 4 && http.status == 200) {
            callback(http.responseText);
        }
    }
    // Открываем соединение и шлем запрос на бэкенд.
    http.open("GET", addr, true);
    http.send(null);
}

function addSelectOption(key, value) {
    let models = value;

    // Получаем из dom-дерева элементы с id x-model, например cpu-model.
    // Это все элементы select, которому надо добавить опции из дб.
    let partType = document.getElementById(key + "-model");
    if (partType == null) {
        return value;
    }

    // Добавление в список компонетов конфигурации для дальнейшего использования.
    partTypes.push(key);

    let hasDefault = false;
    // Проходимся по массиву из моделей для конкретного компонента конфигурации.
    for (let m of models) {
        // Создаем опцию которая будет содержать название модели.
        let opt = document.createElement('option');
        opt.innerHTML = m;

        // Выбираем значение по-умолчанию.
        if (!hasDefault) {
            opt.defaultSelected = true;
            hasDefault = true;
        }

        // Добавляем опцию к селекту.
        partType.appendChild(opt);
    }
    return value;
}

// Код для отправки конфигурации на сервер.

// Добавляем действие по нажатию на submit. Если добавить в html onsubmit,
// скрипт должен быть определен до загрузки формы.
// Но для работы скрипта нужно готовое dom-дерево, которое доступно после
// загрузки страницы.
function addOnsubmitAction() {
    let form = document.getElementById("pc-config-form");
    // form.action = "configured.html";
    form.onsubmit = submit;
}

function submit() {
    // Собираем информацию о конфиге, отображаем и отсылаем на бэкенд.
    let chosenParts = new Map();

    let pretty = ""

    let configName = document.getElementById("config-name").value;
    let configDescription = document.getElementById("description").value;
    chosenParts["name"] = configName;
    chosenParts["description"] = configDescription;
    pretty += "name" + ": " + configName + "<br>";
    pretty += "description" + ": " + configDescription + "<br>";

    for (let key of partTypes) {
        let partType = document.getElementById(key + "-model");
        let idx = partType.options.selectedIndex;
        let val = partType.options[idx].value
        chosenParts[key] = val;

        pretty += key + ": " + val + "<br>";
    }

    let marshalled = JSON.stringify(chosenParts);
    httpPost(backendAddr + "post-config", marshalled)

    // Делаем окно со сформированным конфигом видимым.
    document.getElementById("config-info-bg").style["visibility"] = "visible";
    document.getElementById("config-info-block").style["visibility"] = "visible";
    document.getElementById("hide-config-button").style["visibility"] = "visible";
    document.getElementById("config-info-text").innerHTML = pretty;

    // Делаем окно с конфигом невидимым.
    document.getElementById("hide-config-button").onclick = function () {
        document.getElementById("config-info-bg").style["visibility"] = "hidden";
        document.getElementById("config-info-block").style["visibility"] = "hidden";
        document.getElementById("hide-config-button").style["visibility"] = "hidden";
        document.getElementById("config-info-text").innerHTML = "";
    }
    // Возвращаем false потому что не нужно выполнять action.
    return false
}

function httpPost(addr, body) {
    // Создаем объект для http-запроса.
    let http = new XMLHttpRequest();
    // Создаем функцию-триггер, которая сработает после загрузки ответа от бэкенда.
    http.onreadystatechange = function () {
        if (http.readyState == 4 && http.status != 200) {
            console.log("error. http status:", http.status, "response text:", http.responseText)
        }
    }
    // Открываем соединение и шлем запрос на бэкенд.
    http.open("POST", addr, true);
    http.send(body);
}
