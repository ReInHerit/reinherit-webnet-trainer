document.addEventListener('DOMContentLoaded', function () {

    loadLabels();
    if(selectedConcepts.length > 0) {
        $("#concepts-container").toggle();
        $("#inf-train-container").toggle();
    }

    loadAllDatasets();
    loadDataset("exampleImages");
    canvas = document.getElementById("canvas");

    loadAvailModels();

    $("#add-label").click(function () {
        var button = this;
        $(this).hide();
        var input = document.createElement("input");
        input.setAttribute("class", "input-label");
        input.setAttribute("type", "text");
        input.setAttribute("placeholder", "Insert name");
        document.getElementById("concepts-list").append(input);
        input.select();
        $(input).change(function () {
            this.parentNode.removeChild(this);
            addLabel(input.value);
            $(button).show();
        });
    });

    $("#select-all-concepts").click(function () {
        var list = document.querySelectorAll(".concept");
        list.forEach((checkbox) => {
            checkbox.checked = true;
        });
        $(this).hide();
        $("#deselect-all-concepts").show();
    });

    $("#deselect-all-concepts").click(function () {
        var list = document.querySelectorAll(".concept");
        list.forEach((checkbox) => {
            checkbox.checked = false;
        });
        $(this).hide();
        $("#select-all-concepts").show();
    });

    $('#submit-concepts').click(function () {
        saveConcepts();
        $("#concepts-container").slideToggle();
        $("#inf-train-container").slideToggle();
    });

    $("#revise-concepts").click(function () {
        selectedConcepts = [];
        $("#inf-train-container").slideToggle();
        $("#concepts-container").slideToggle();
    });

    $("#inference-button").click(function() {
        annotateAll();
    });

    $("#load-button").click(function () {
        $("#upload-container").slideToggle();
    });

    $("#submit-dataset").click(function () {
        uploadDataset();
        $("#upload-container").slideToggle();
    });

    $("#dataset-select").change(function () {
        loadDataset(this.value);
    });

    $("#next-page").click(function () {
        var oldPage = parseInt(document.querySelector(".active").innerHTML);
        if(oldPage < this.parentNode.children.length - 2) {
            var datasetName = document.getElementById("dataset-select").value;
            loadImages(datasetName, oldPage + 1);
            $(".active").removeClass("active");
            $(this.parentNode.children[oldPage + 1]).addClass("active");
        }
    });
    $("#previous-page").click(function () {
        var oldPage = parseInt(document.querySelector(".active").innerHTML);
        if(oldPage > 1) {
            datasetName = document.getElementById("dataset-select").value;
            loadImages(datasetName, oldPage - 1);
            $(".active").removeClass("active");
            $(this.parentNode.children[oldPage - 1]).addClass("active");
        }
    })
    
    $("#add-bbox").click(function () {
        this.disabled = true;
        this.style.backgroundColor = "#e0e0e0";
        addBbox();
    });

    $("#info").hover(function () {
        $("#bboxes-info").toggle()
    }, function() {
        $("#bboxes-info").toggle();
    })

    $("#reset-button").click(function () {
        deleteAllBboxes();
    });

    $("#inference-single-button").click(function () {
        img = document.getElementById("img-ann");
        annotateImage(img.getAttribute("src"));
    })

    $("#canvas").click(function () {
        if(selectedBox !== undefined) {
            deselectBbox();
        }
    });

    $("#save-button").click(function () {
        var button = document.getElementById("add-bbox");
        if(button.disabled === true) {
            button.disabled = false;
            button.style.backgroundColor = "#2297f5";
        }
        saveImageData();
        loadMiniatureData();
        saveImageAnnotations();
        deselectImage();
        backHome();
    });

    $("#exit-button").click(function() {
        var button = document.getElementById("add-bbox");
        if(button.disabled === true) {
            button.disabled = false;
            button.style.backgroundColor = "#2297f5";
        }
        saveImageData();
        loadMiniatureData();
        saveImageAnnotations();
        deselectImage();
        backHome();
    });

    $("#model-select").change(function () {
        selectedModel = this.value;
    });

    $("#training-button").click(function () {

        startTraining();
        $(this).css("display", "none");
        $("#monitor-training-button").css("display", "block");
    });

    $("#monitor-training-button").click(function () {
        openTrainingPage();
    })

    $("#back-button").click(function () {
        hideTraining();
    });

    $("#background-button").click(function () {
        hideTraining();
    })
});

var selectedImage;
var selectedTitle;
var selectedAuthor;

var selectedDataset;

var canvas;
var startPointX;
var startPointY;
var finalPointX;
var finalPointY;
var mouseIsDown = false;
var concepts = [];
var selectedConcepts = [];
var bboxes = [];
var selectedBox;
var resizeRatio;
var selectedModel;

var dragItem;
var active = false;
var dx;
var dy;
var initialX;
var initialY;
var offLeft;
var offTop;

var resizeItem;
var oldWidth;
var oldHeight;
var oldStartY;
var oldStartX;
var initX;
var initY;

function resizeImg(img, MAX_WIDTH, MAX_HEIGHT, MIN_WIDTH, MIN_HEIGHT) {
    var width, height;
    width = img.width;
    height = img.height;
    var ratio = width / height;

    if(width > MAX_WIDTH) {
        width = MAX_WIDTH;
        height = width / ratio;
        if(height > MAX_HEIGHT) {
            height = MAX_HEIGHT;
            width = height * ratio;
        }
    }
    if(width < MIN_WIDTH) {
        width = MIN_WIDTH;
        height = width / ratio;
        if(height < MIN_HEIGHT) {
            height = MIN_HEIGHT;
            width = height * ratio;
        }
    }
    if(height > MAX_HEIGHT) {
        height = MAX_HEIGHT;
        width = height * ratio;
        if(width > MAX_WIDTH) {
            width = MAX_WIDTH;
            height = width / ratio;
        }
    }
    if(height < MIN_HEIGHT) {
        height = MIN_HEIGHT;
        width = height * ratio;
        if(width < MIN_WIDTH) {
            width = MIN_WIDTH;
            height = width / ratio;
        }
    }
    return [width, height];
}

function openImage(image) {
    if(selectedConcepts.length === 0) {
        alert("Select at least one concepts!");
        return;
    }
    console.log(concepts);
    var src = image.getAttribute("src");
    var img = document.createElement("img");
    img.id = "img-ann";
    img.setAttribute("src", src);

    var data;
    $.ajax({
        type: "POST",
        async: false,
        url: "/load-image-data",
        data: JSON.stringify(src),
        contentType: "application/json",
        dataType: 'json',
        success: function(result) {
            data = result;
        }
    })
    if(data[0][2] !== null) {
        document.getElementById("title").value = data[0][2];
    }
    if(data[0][3] !== null) {
        document.getElementById("author").value = data[0][3];
    }
    if(data[0][4] !== null) {
        document.getElementById("description").value = data[0][4];
    }

    let width;
    let height;

    const MAX_WIDTH = window.innerWidth / 2;
    const MAX_HEIGHT = window.innerHeight - 130;
    const MIN_WIDTH = window.innerWidth / 3;
    const MIN_HEIGHT = window.innerHeight / 2;

    let newSize = resizeImg(img, MAX_WIDTH, MAX_HEIGHT, MIN_WIDTH, MIN_HEIGHT);
    width = newSize[0];
    height = newSize[1];
    resizeRatio = width / img.width;

    img.width = width;
    img.height = height;
    canvas.width = width;
    canvas.height = height;
    $(".main-container").css("display", "none");
    $("#canvas-container").css({
        "width": width,
        "height": height
    });
    $("#img-ann").css({
        "position": "absolute",
        "z-index": 0
    })
    document.getElementById("canvas-container").append(img, document.getElementById("canvas"));
    $("#ann-commands").css("height", height);
    $("#single-image-container").css("display", "block");

    displayBboxes(src);
}

function displayBboxes(filename) {
    var annotations;

    $.ajax({
        type: "POST",
        async: false,
        url: "/load-image-annotations",
        data: JSON.stringify(filename),
        contentType: "application/json",
        dataType: 'json',
        success: function(result) {
            annotations = result;
        }
    })
    console.log(annotations);
    let i;
    for(i = 0; i < annotations.length; i++) {
        if(selectedConcepts.includes(annotations[i][2])) {
            displayBbox(annotations[i], resizeRatio);
        }
    }
}

function displayBbox(boxData, resizeRatio) {
    let label = document.createElement("select");
    label.className = "label";
    let option;
    for (var i in selectedConcepts) {
        option = document.createElement("option");
        option.setAttribute("value", selectedConcepts[i]);
        option.innerHTML = selectedConcepts[i];
        label.append(option);
    }
    label.value = boxData[2];

    var deleter = document.createElement("BUTTON");
    $(deleter).addClass("bbox-deleter");
    deleter.innerHTML = "&#10006;"
    var container = document.getElementById("bboxes-container");
    container.append(label);
    container.append(deleter);
    var newBbox = [label.value, boxData[4], boxData[5], boxData[6], boxData[7], boxData[8]];
    bboxes.push(newBbox);

    var box = document.createElement("DIV");
    box.innerHTML = label.value;
    $(box).addClass("bbox")
    $(box).css({
        "left": boxData[4] * resizeRatio,
        "top": boxData[5] * resizeRatio,
        "width": boxData[6] * resizeRatio,
        "height": boxData[7] * resizeRatio
    })
    if(boxData[8] === 1) {
        $(box).css("background-color", "rgba(178,80,6,0.6)");
        $(label).css("border-color", "rgba(178,80,6,0.6)");
        $(deleter).css("border-color", "rgba(178,80,6,0.6)");
    }
    $("#canvas-container").append(box);
    $(".bbox").show();

    box.addEventListener("mousedown", function (e) {
        dragItem = this;
        dragStart(e);
        document.addEventListener("mouseup", dragEnd, false);
        document.addEventListener("mousemove", drag, false);
    });

    buildResizers(box);

    $(box).hover(function(){
        var color = window.getComputedStyle(box).backgroundColor;
        label.style.backgroundColor = color;
        label.style.color = "white";
        deleter.style.backgroundColor = color;
        deleter.style.color = "white";
        }, function(){
        label.style.backgroundColor = null;
        label.style.color = null;
        deleter.style.backgroundColor = null;
        deleter.style.color = null;
    });

    $(deleter).hover(function(){
        box.style.opacity = 0.6;
    }, function(){
        box.style.opacity = null;
    });

    deleter.addEventListener("click", function() { 
        deleteBbox(box)
    });

    $(label).hover(function(){
        box.style.opacity = 0.6;
    }, function(){
        box.style.opacity = null;
    });

    label.addEventListener("change", function() {
        box.innerHTML = this.value;
        var index = getBboxIndex(box);
        bboxes[index][0] = label.value;
    });
}

function selectImage(image) {
    var selectedContainer = image.parentNode;
    selectedImage = image;
    selectedTitle = selectedContainer.children[0];
    selectedAuthor = selectedContainer.children[1];
}

function deselectImage() {
    selectedImage = undefined;
    selectedTitle = undefined;
    selectedAuthor = undefined;
}

function addBbox() {
    let label = document.createElement("select");
    label.className = "label";
    let option;
    for (const i in selectedConcepts) {
        option = document.createElement("option");
        option.setAttribute("value", selectedConcepts[i]);
        option.innerHTML = selectedConcepts[i];
        label.append(option);
    }
    var deleter = document.createElement("BUTTON");
    deleter.innerHTML = "&#10006;";
    $(deleter).addClass("bbox-deleter");
    var container = document.getElementById("bboxes-container");
    container.append(label);
    container.append(deleter);
    
    $(".bbox").hide();

    canvas.style.cursor = "crosshair";

    canvas.addEventListener('mousedown', function(e) {
        getCoordinates(e);
        canvas.removeEventListener('mousedown', arguments.callee);
    });
    canvas.addEventListener('mouseup', function(e) {
        getCoordinates(e);
        canvas.removeEventListener('mouseup', arguments.callee);
    });
    canvas.addEventListener('mouseout', function(e) {
        getCoordinates(e);
        canvas.removeEventListener('mouseout', arguments.callee);
    });
}

function getCoordinates(e) {
    var canv = $("#canvas-container")
    var offset = canv.offset();
    switch (e.type) {
        case 'mousedown':
            mouseIsDown = true;
            startPointX = e.clientX - offset.left;
            startPointY = e.clientY - offset.top;
            break;
        case 'mouseup':
            if(mouseIsDown) {
                mouseIsDown = false;
                finalPointX = e.clientX - offset.left;
                finalPointY = e.clientY - offset.top;
                drawBbox();
            }
            break;
        case 'mouseout':
            if (mouseIsDown) {
                mouseIsDown = false;
                finalPointX = e.clientX - offset.left;
                finalPointY = e.clientY - offset.top;
                drawBbox();
            }
            break;
    }
}

function drawBbox() {
    let tmp;
    if (startPointX > finalPointX) {
        tmp = startPointX;
        startPointX = finalPointX;
        finalPointX = tmp;
    }
    if (startPointY > finalPointY) {
        tmp = startPointY;
        startPointY = finalPointY;
        finalPointY = tmp;
    }

    if(finalPointX > canvas.width){
        finalPointX = canvas.width;
    }
    if(startPointX < 0) {
        startPointX = 0;
    }
    if(finalPointY > canvas.height) {
        finalPointY = canvas.height;
    }
    if(startPointY < 0) {
        startPointY = 0;
    }

    var labels = document.getElementsByClassName("label");
    var label = labels.item(labels.length - 1);
    var newBbox = [
        label.value, startPointX / resizeRatio, startPointY / resizeRatio, (finalPointX - startPointX) / resizeRatio,
            (finalPointY - startPointY) / resizeRatio, 0];
    bboxes.push(newBbox);

    var box = document.createElement("DIV");
    box.innerHTML = label.value;
    box.setAttribute("class", "bbox");
    $(box).css({
        "left": startPointX,
        "top": startPointY,
        "width": finalPointX - startPointX,
        "height": finalPointY - startPointY,
    })
    $("#canvas-container").append(box);
    $(".bbox").show();
    canvas.style.cursor = "default";
    var button = document.getElementById("add-bbox");
    button.disabled = false;
    button.style.backgroundColor = "#2297f5";

    //DRAG BBOX
    box.addEventListener("mousedown", function (e) {
        dragItem = this;
        dragStart(e);
        document.addEventListener("mouseup", dragEnd, false);
        document.addEventListener("mousemove", drag, false);
    });

    buildResizers(box);

    var deleter = document.getElementsByClassName("bbox-deleter").item(labels.length - 1);

    $(box).hover(function(){
        var color = window.getComputedStyle(box).backgroundColor;
        label.style.backgroundColor = color;
        label.style.color = "white";
        deleter.style.backgroundColor = color;
        deleter.style.color = "white";
        }, function(){
        label.style.backgroundColor = null;
        label.style.color = null;
        deleter.style.backgroundColor = null;
        deleter.style.color = null;
    });

    $(deleter).hover(function(){
        box.style.opacity = 0.6;
    }, function(){
        box.style.opacity = null;
    });

    deleter.addEventListener("click", function() { 
        deleteBbox(box)
    });

    $(label).hover(function(){
        box.style.opacity = 0.6;
    }, function(){
        box.style.opacity = null;
    });

    label.addEventListener("change", function() {
        box.innerHTML = this.value;
        var index = getBboxIndex(box);
        bboxes[index][0] = label.value;
        buildResizers(box);
    });
}

function dragStart(e) {
    var position = $(dragItem).position();
    offLeft = position.left;
    offTop = position.top;
    initialX = e.clientX;
    initialY = e.clientY;
  
    if (e.target === dragItem) {
        active = true;
    }
}

function dragEnd() {
    var index = getBboxIndex(dragItem);
    var newPosition = $(dragItem).position();
    bboxes[index][1] = newPosition.left / resizeRatio;
    bboxes[index][2] = newPosition.top / resizeRatio;
    document.removeEventListener("mouseup", dragEnd, false);
    document.removeEventListener("mousemove", drag, false);
    active = false;
}

function drag(e) {
    if (active) {
        e.preventDefault();
        dx = e.clientX - initialX;
        dy = e.clientY - initialY;
    }
    
    var newLeft = offLeft + dx;
    var newTop = offTop + dy;
    if (newLeft < 0) {
        newLeft = 0;
        dragEnd();
    }
    if (newTop < 0) {
        newTop = 0;
        dragEnd();
    }
    if (newLeft + $(dragItem).width() > canvas.width) {
        newLeft = canvas.width - $(dragItem).width();
        dragEnd();
    }
    if (newTop + $(dragItem).height() > canvas.height) {
        newTop = canvas.height - $(dragItem).height();
        dragEnd();
    }

    $(dragItem).css({
        "left": newLeft,
        "top": newTop
    });
}

function buildResizers(box) {
    var resizerR = document.createElement("div");
    var resizerB = document.createElement("div");
    var resizerT = document.createElement("div");
    var resizerL = document.createElement("div");
    resizerR.setAttribute("class", "resizer");
    resizerB.setAttribute("class", "resizer");
    resizerT.setAttribute("class", "resizer");
    resizerL.setAttribute("class", "resizer");
    $(resizerR).css({
        "top": 0,
        "right": 0,
        "height": "100%",
        "width": "5px",
        "cursor": "ew-resize"
    })
    $(resizerB).css({
        "bottom": 0,
        "left": 0,
        "height": "5px",
        "width": "100%",
        "cursor": "ns-resize"
    })
    $(resizerT).css({
        "top": 0,
        "left": 0,
        "height": "5px",
        "width": "100%",
        "cursor": "ns-resize"
    })
    $(resizerL).css({
        "top": 0,
        "left": 0,
        "height": "100%",
        "width": "5px",
        "cursor": "ew-resize"
    })
    box.append(resizerR);
    box.append(resizerB);
    box.append(resizerT);
    box.append(resizerL);
    resizerR.addEventListener("mousedown", function(e) {
        e.stopPropagation();
        resizeItem = box;
        resizeRStart(e);
        document.addEventListener("mouseup", resizeREnd, false);
        document.addEventListener("mousemove", resizeR, false);
    });
    resizerB.addEventListener("mousedown", function(e) {
        e.stopPropagation();
        resizeItem = box;
        resizeBStart(e);
        document.addEventListener("mouseup", resizeBEnd, false);
        document.addEventListener("mousemove", resizeB, false);
    });
    resizerT.addEventListener("mousedown", function(e) {
        e.stopPropagation();
        resizeItem = box;
        resizeBStart(e);
        document.addEventListener("mouseup", resizeTEnd, false);
        document.addEventListener("mousemove", resizeT, false);
    });
    resizerL.addEventListener("mousedown", function(e) {
        e.stopPropagation();
        resizeItem = box;
        resizeRStart(e);
        document.addEventListener("mouseup", resizeLEnd, false);
        document.addEventListener("mousemove", resizeL, false);
    });
}

function resizeRStart(e) {
    oldWidth = $(resizeItem).width();
    oldStartX = $(resizeItem).position().left;
    initX = e.clientX;
    active = true;
}

function resizeBStart(e) {
    oldHeight = $(resizeItem).height();
    oldStartY = $(resizeItem).position().top;
    initY = e.clientY;
    active = true;
}

function resizeREnd() {
    var index = getBboxIndex(resizeItem);
    var newWidth = $(resizeItem).width();
    bboxes[index][3] = newWidth / resizeRatio;
    document.removeEventListener("mouseup", resizeREnd, false);
    document.removeEventListener("mousemove", resizeR, false);
    active = false;
}

function resizeLEnd() {
    var index = getBboxIndex(resizeItem);
    var newWidth = $(resizeItem).width();
    var newStartX = $(resizeItem).position().left;
    bboxes[index][3] = newWidth / resizeRatio;
    bboxes[index][1] = newStartX / resizeRatio;
    document.removeEventListener("mouseup", resizeLEnd, false);
    document.removeEventListener("mousemove", resizeL, false);
    active = false;
}

function resizeBEnd() {
    var index = getBboxIndex(resizeItem);
    var newHeight = $(resizeItem).height();
    bboxes[index][4] = newHeight / resizeRatio;
    document.removeEventListener("mouseup", resizeBEnd, false);
    document.removeEventListener("mousemove", resizeB, false);
    active = false;
}

function resizeTEnd() {
    var index = getBboxIndex(resizeItem);
    var newHeight = $(resizeItem).height();
    var newStartY = $(resizeItem).position().top;
    bboxes[index][2] = newStartY / resizeRatio;
    bboxes[index][4] = newHeight / resizeRatio;
    document.removeEventListener("mouseup", resizeTEnd, false);
    document.removeEventListener("mousemove", resizeT, false);
    active = false;
}

function resizeR(e) {
    if (active) {
        e.preventDefault();
        dx = e.clientX - initX;
    }
    var newWidth = oldWidth + dx;
    if (newWidth < 0) {
        newWidth = 1;
    }
    if ($(resizeItem).position().left + newWidth > canvas.width) {
        newWidth = canvas.width - $(resizeItem).position().left;
    }
    $(resizeItem).width(newWidth);
}

function resizeL(e) {
    if (active) {
        e.preventDefault();
        dx = e.clientX - initX;
    }
    var newWidth = oldWidth - dx;
    var newStartX = oldStartX + dx;
    if (newWidth < 0) {
        newWidth = 1;
        newStartX = oldStartX + oldWidth - 1;
    }
    if (newStartX < 0) {
        newStartX = 0;
        newWidth = oldStartX + oldWidth;
    }
    $(resizeItem).width(newWidth);
    $(resizeItem).css("left", newStartX);
}

function resizeB(e) {
    if (active) {
        e.preventDefault();
        dy = e.clientY - initY;
    }
    var newHeight = oldHeight + dy;
    if (newHeight < 0) {
        newHeight = 1;
    }
    if ($(resizeItem).position().top + newHeight > canvas.height) {
        newHeight = canvas.height - $(resizeItem).position().top;
    }
    $(resizeItem).height(newHeight);
}

function resizeT(e) {
    if (active) {
        e.preventDefault();
        dy = e.clientY - initY;
    }
    var newHeight = oldHeight - dy;
    var newStartY = oldStartY + dy;
    console.log(newStartY);
    if (newHeight < 0) {
        newHeight = 1;
        newStartY = oldStartY + oldHeight - 1;
    }
    if (newStartY < 0) {
        newStartY = 0;
        newHeight = oldStartY + oldHeight;
    }
    $(resizeItem).height(newHeight);
    $(resizeItem).css("top", newStartY);
}

function deleteAllBboxes() {
    var boxes = document.getElementsByClassName("bbox");
    var labels = document.getElementsByClassName("label");
    var deleters = document.getElementsByClassName("bbox-deleter");
    while(boxes[0]) {
        boxes[0].parentNode.removeChild(boxes[0]);
    }
    while(labels[0]) {
        labels[0].parentNode.removeChild(labels[0]);
    }
    while(deleters[0]){
        deleters[0].parentNode.removeChild(deleters[0]);
    }
    bboxes = [];
}

function getBboxIndex(box) {
    var allBoxes = box.parentNode.getElementsByClassName("bbox");
    var found = false;
    var i = 0;
    while(found === false && allBoxes[i]) {
        if(allBoxes[i] === box){
            found = true;
        }
        else {
            i++;
        }
    }
    return i;
}

function selectBbox(box) {
    if(selectedBox === box){
        console.log("ciao");
        return;
    }
    if(selectedBox !== undefined) {
        deselectBbox();
    }
    box.style.opacity = "0.8";
    var index = getBboxIndex(box);
    var label = document.getElementsByClassName("label")[index];
    var deleter = document.getElementsByClassName("bbox-deleter")[index];
    label.style.border = "2px solid #2297f5"
    deleter.style.borderColor = "#2297f5"
    selectedBox = box;
}

function deselectBbox() {
    selectedBox.style.opacity = "0.6";
    var index = getBboxIndex(selectedBox);
    var label = document.getElementsByClassName("label")[index];
    label.style.border = "1px solid black";
    var deleter = document.getElementsByClassName("bbox-deleter")[index];
    deleter.style.border = "1px solid black";
    selectedBox.addEventListener("click", function() {
        selectBbox(this);
    })
    selectedBox = undefined;
}

function deleteBbox(box) {
    var index = getBboxIndex(box);
    box.parentNode.removeChild(box);
    var label = document.getElementsByClassName("label")[index];
    label.parentNode.removeChild(label);
    var boxDeleter = document.getElementsByClassName("bbox-deleter")[index];
    boxDeleter.parentNode.removeChild(boxDeleter);
    bboxes.splice(index, 1);
    selectedBox = undefined;
}

function backHome() {
    $("#single-image-container").css("display", "none");
    $(".main-container").css("display", "block");
    document.getElementById("canvas-container").removeChild(document.getElementById("img-ann"));
    deleteAllBboxes();
    document.getElementById("title").value = "";
    document.getElementById("author").value = "";
    document.getElementById("description").value = "";
}

function saveImageData() {
    var filename = document.getElementById("img-ann").getAttribute("src");
    var title = document.getElementById("title").value;
    var author = document.getElementById("author").value;
    var description = document.getElementById("description").value;
    var server_data = [
        {"filename": filename},
        {"title": title},
        {"author": author},
        {"description": description}
    ];

    $.ajax({
        type: "POST",
        url: "/process-data",
        async: false,
        data: JSON.stringify(server_data),
        contentType: "application/json",
        dataType: 'json',
        success: function(result) {
            console.log("Image data stored");
          } 
    });
}

function saveImageAnnotations() {
    var filename = document.getElementById("img-ann").getAttribute("src");
    var server_data = [];
    if(bboxes.length === 0) {
        resetImageAnnotations(filename);
        return;
    }
    for(box in bboxes) {
        var area = bboxes[box][3] * bboxes[box][4];
        var server_box = [
            {"image_name": filename},
            {"category": bboxes[box][0]},
            {"area": area},
            {"x_min": bboxes[box][1]},
            {"y_min": bboxes[box][2]},
            {"width": bboxes[box][3]},
            {"height": bboxes[box][4]},
            {"automatic": bboxes[box][5]}
        ];
        server_data.push(server_box);
    }

    $.ajax({
        type: "POST",
        url: "/process-annotations",
        async: false,
        data: JSON.stringify(server_data),
        contentType: "application/json",
        dataType: 'json',
        success: function(result) {
            console.log("Annotations stored");
          } 
    });
}

function resetImageAnnotations(filename) {
    $.ajax({
        type: "POST",
        url: "/reset-image-annotations",
        async: false,
        data: JSON.stringify(filename),
        contentType: "application/json",
        dataType: 'json',
        success: function(result) {
            console.log("Annotations removed");
          } 
    });
}

function loadMiniatureData() {
    var filename = document.getElementById("img-ann").getAttribute("src");
    var data;

    $.ajax({
        type: "POST",
        async: false,
        url: "/load-image-data",
        data: JSON.stringify(filename),
        contentType: "application/json",
        dataType: 'json',
        success: function(result) {
            data = result;
        }
    })

    if(data[0][2] !== null) {
        selectedTitle.value = data[0][2];
    }
    if(data[0][3] !== null) {
        selectedAuthor.value = data[0][3];
    }

}

function updateMiniatureData(input) {
    var title = input.parentNode.children[0].value;
    var author = input.parentNode.children[1].value;
    var img = input.parentNode.children[2].getAttribute('src');

    var server_data = [
        {"image_name": img},
        {"title": title},
        {"author": author}
    ];

    $.ajax({
        type: "POST",
        async: false,
        url: "/save-miniature-data",
        data: JSON.stringify(server_data),
        contentType: "application/json",
        dataType: 'json',
        success: function(result) {
            console.log("Updated miniature data");
        }
    })
}

function loadAllDatasets() {
    var select = document.getElementById("dataset-select");
    var datasets;

    $.ajax({
        type: "POST",
        async: false,
        url: "/load-all-datasets",
        contentType: "application/json",
        dataType: 'json',
        success: function(result) {
            datasets = result;
        }
    })

    for(let i = 0; i < datasets.length; i++) {
        var newDataset = document.createElement("option");
        var datasetName = datasets[i];
        newDataset.setAttribute("value", datasetName);
        newDataset.innerHTML = datasetName;
        select.append(newDataset);
    }
}

function uploadDataset() {
    var form_data = new FormData();
    var datasetName = document.getElementById("dataset-name").value;
    var ins = document.getElementById('input-dataset').files.length;
        
    if(ins === 0) {
        alert("Select one or more files");
        return;
    }

    $.ajax({
        type: "POST",
        async: false,
        url: "/create-dataset",
        data: JSON.stringify(datasetName),
        contentType: "application/json",
        dataType: 'json',
        success: function(result) {
            console.log(result)
        }
    })
        
    for (var x = 0; x < ins; x++) {
        form_data.append("files[]", document.getElementById('input-dataset').files[x]);
    }
        
    $.ajax({
        url: 'save-images', // point to server-side URL
        dataType: 'json', // what to expect back from server
        async: false,
        cache: false,
        contentType: false,
        processData: false,
        data: form_data,
        type: 'POST',
        success: function (response) { // display success response
            console.log("Succesfully uploaded")
        }
    });

    var select = document.getElementById("dataset-select");
    var newDataset = document.createElement("option");
    newDataset.setAttribute("value", datasetName);
    newDataset.innerHTML = datasetName;
    select.append(newDataset);

    loadDataset(datasetName);
}

function loadDataset(datasetName) {
    var select = document.getElementById("dataset-select");
    select.value = datasetName;
    var numImages;
    
    $.ajax({
        type: "POST",
        async: false,
        url: "/load-dataset",
        data: JSON.stringify(datasetName),
        contentType: "application/json",
        dataType: 'json',
        success: function(result) {
            numImages = result;
        }
    })

    var numPages = Math.ceil(numImages / 9);
    console.log(numPages);

    var oldPages = document.getElementsByClassName("images-page");
    while(oldPages[0]) {
        oldPages[0].parentNode.removeChild(oldPages[0]);
    }

    for(let i = 1; i <= numPages; i++) {
        var page = document.createElement("div");
        if(i === 1) {
            page.setAttribute("class", "images-page active");
        } else {
            $(page).addClass("images-page");
        }
        page.innerHTML = i;
        page.style.marginRight = "5px";
        document.getElementById("pagination").append(page, document.getElementById("next-page"));
    }

    $(".images-page").click(function () {
        datasetName = document.getElementById("dataset-select").value;
        loadImages(datasetName, parseInt(this.innerHTML));
        $(".active").removeClass("active");
        $(this).addClass("active");
    })

    loadImages(datasetName, 1);
}

function loadImages(datasetName, page) {
    var oldContainers = document.getElementsByClassName("miniature-container");
    while(oldContainers[0]) {
        oldContainers[0].parentNode.removeChild(oldContainers[0]);
    }
    var images;
    var server_data = [
        {"dataset_name": datasetName},
        {"page": page}
    ]

    $.ajax({
        type: "POST",
        async: false,
        url: "/load-images-page",
        data: JSON.stringify(server_data),
        contentType: "application/json",
        dataType: 'json',
        success: function(result) {
            images = result;
        }
    })

    for(let i in images) {
        var container = document.createElement("div");
        container.setAttribute("class", "miniature-container");
        var img = document.createElement("img");
        img.setAttribute("src", images[i][1]);
        img.setAttribute("class", "miniature");
        img.setAttribute("alt", "image preview");
        var title = document.createElement("input");
        title.setAttribute("class", "miniature-input");
        title.setAttribute("type", "text");
        title.setAttribute("placeholder", "Title");
        if(images[i][2] !== null) {
            title.setAttribute("value", images[i][2]);
        }
        var author = document.createElement("input");
        author.setAttribute("class", "miniature-input");
        author.setAttribute("type", "text");
        author.setAttribute("placeholder", "Author");
        if(images[i][3] !== null) {
            author.setAttribute("value", images[i][3]);
        }

        document.getElementById("images-container").append(container);
        container.append(title);
        container.append(author);
        container.append(img);
        
        $(img).click(function () {
            selectImage(this);
            openImage(this);
        });

        $(title).change(function () {
            updateMiniatureData(this);
        });
        $(author).change(function () {
            updateMiniatureData(this);
        });
    }
}

function loadLabels() {
    var allCategories;
    var selectedCategories;
    var labels = [];
    var selectedLabels = [];
    
    $.ajax({
        type: "POST",
        async: false,
        url: "/load-labels",
        contentType: "application/json",
        dataType: 'json',
        success: function(result) {
            allCategories = result;
        }
    })

    $.ajax({
        type: "POST",
        async: false,
        url: "/load-selected-labels",
        contentType: "application/json",
        dataType: 'json',
        success: function(result) {
            selectedCategories = result;
        }
    })

    for(i = 0; i < allCategories.length; i++) {
        labels.push(allCategories[i][0]);
    }

    for(i = 0; i < selectedCategories.length; i++) {
        selectedLabels.push(selectedCategories[i][0]);
    }
    console.log(selectedLabels);

    var container = document.getElementById("concepts-list")
    var label;
    for(label in labels) {
        var newRow = document.createElement("div");
        newRow.setAttribute("class", "concept-row");
        var newLabel = document.createElement("input");
        newLabel.setAttribute("class", "concept");
        newLabel.setAttribute("id", labels[label]);
        newLabel.setAttribute("type", "checkbox");
        newLabel.setAttribute("name", labels[label]);
        newLabel.setAttribute("value", labels[label]);
        if(selectedLabels.includes(labels[label])) {
            newLabel.checked = true;
        }
        var text = document.createElement('label');
        text.htmlFor = labels[label];
        text.appendChild(document.createTextNode(labels[label]));
        container.append(newRow, document.getElementById("add-label"));
        newRow.append(newLabel);
        newRow.append(text);
    }
    concepts = labels;
    selectedConcepts = selectedLabels;
}

function addLabel(categoryName) {
    var container = document.getElementById("concepts-list");
    var newRow = document.createElement("div");
    newRow.setAttribute("class", "concept-row");
    var newLabel = document.createElement("input");
    newLabel.setAttribute("class", "concept");
    newLabel.setAttribute("id", categoryName);
    newLabel.setAttribute("type", "checkbox");
    newLabel.setAttribute("name", categoryName);
    newLabel.setAttribute("value", categoryName);
    var text = document.createElement('label');
    text.htmlFor = categoryName;
    text.appendChild(document.createTextNode(categoryName));
    container.append(newRow, document.getElementById("add-label"));
    newRow.append(newLabel);
    newRow.append(text);

    concepts.push(categoryName);

    $.ajax({
        type: "POST",
        async: false,
        url: "/add-label",
        data: JSON.stringify(categoryName),
        contentType: "application/json",
        dataType: 'json',
        success: function(result) {
            console.log("New concept stored")
        }
    })
}

function saveConcepts() {
    var values = document.querySelectorAll(".concept:checked");
    values.forEach((checkbox) => {
        selectedConcepts.push(checkbox.value);
    });
    console.log(selectedConcepts);

    $.ajax({
        type: "POST",
        async: false,
        url: "/set-categories",
        data: JSON.stringify(selectedConcepts),
        contentType: "application/json",
        dataType: 'json',
        success: function(result) {
            console.log("Concepts stored")
        }
    })
}

function loadAvailModels() {
    var server_data;

    $.ajax({
        type: "POST",
        async: false,
        url: "/load-models",
        data: JSON.stringify(),
        contentType: "application/json",
        dataType: 'json',
        success: function(results) {
            server_data = results
        }
    })
    var models = []
    for (let i in server_data) {
        models.push(server_data[i][0]);
    }
    console.log(models);
    var select = document.getElementById("model-select");
    for(let i in models) {
        var model = document.createElement("option");
        model.setAttribute("value", models[i]);
        model.innerHTML = models[i];
        select.append(model);
    }
    select.value = models[0];
    selectedModel = select.value;
}

function annotateAll() {
    var datasetName = document.getElementById("dataset-select").value;
    var loader = document.createElement("div");
    loader.setAttribute("class", "loader");
    var container = document.getElementById("inference-content");
    container.append(loader);
    document.body.style.pointerEvents = "none";
    var server_data = [
        {'dataset_name': datasetName},
        {'model': selectedModel}
    ]
    
    $.ajax({
        type: "POST",
        async: true,
        url: "/inference",
        data: JSON.stringify(server_data),
        contentType: "application/json",
        dataType: 'json',
        success: function(result) {
            container.removeChild(loader);
            document.body.style.pointerEvents = "auto";
        },
        error: function(result, errorThrown) {
            alert("Annotation failed")
            container.removeChild(loader);
            document.body.style.pointerEvents = "auto";
        }
    })
}

function annotateImage(filename) {
    var loader = document.createElement("div");
    loader.setAttribute("class", "loader");
    var container = document.getElementById("bboxes-container");
    container.append(loader);
    var button = document.getElementById("inference-single-button");
    button.innerHTML = "Annotating...";
    document.body.style.pointerEvents = "none";
    var server_data = [
        {'filename': filename},
        {'model': selectedModel}
    ]

    $.ajax({
        type: "POST",
        async: true,
        url: "/inference-single-image",
        data: JSON.stringify(server_data),
        contentType: "application/json",
        dataType: 'json',
        success: function(result) {
            document.getElementById("inference-single-button").innerHTML = "Annotate";
            document.body.style.pointerEvents = "auto";
            button.innerHTML = "Annotate";
            container.removeChild(loader);
            displayBboxes(filename);
        },
        error: function(result, errorThrown) {
            alert("Annotation failed")
            document.getElementById("inference-single-button").innerHTML = "Annotate";
            document.body.style.pointerEvents = "auto";
            button.innerHTML = "Annotate";
            container.removeChild(loader);
        }
    })
}

function openTrainingPage() {
    $(".main-container").css("display", "none");
    $("#training-page").css("display", "block");
}

function hideTraining() {
    $(".main-container").css("display", "block");
    $("#training-page").css("display", "none");
}

function startTraining() {
    var datasetName = document.getElementById("dataset-select").value;
    document.getElementById("selected-dataset").innerHTML = datasetName;
    document.getElementById("selected-model").innerHTML = selectedModel;
    var confirmText = 'Training will start and it could take a lot of time\nClick "OK" to continue';
    var list = document.getElementById("progress-list");
    if (confirm(confirmText) === true) {
        $("#train-p").slideToggle();
        var info = document.createElement("div");
        info.setAttribute("class", "info-training")
        info.innerHTML = "Training started...";
        var container = document.getElementById("training-content");
        container.append(info);

        var server_data = [
            {"dataset_name": datasetName},
            {"model": selectedModel}
        ];

        var annotated = document.createElement("li");
        annotated.innerHTML = "Processing annotations...";
        list.append(annotated)

        $.ajax({
            type: "POST",
            async: true,
            url: "/save-annotations",
            data: JSON.stringify(datasetName),
            contentType: "application/json",
            dataType: 'json',
            success: function(result) {
                annotated.innerHTML = "Annotations saved correctly";
                var augmented = document.createElement("li");
                augmented.innerHTML = "Augmentation started...";
                list.append(augmented);

                $.ajax({
                    type: "POST",
                    async: true,
                    url: "/augment-images",
                    data: JSON.stringify(datasetName),
                    contentType: "application/json",
                    dataType: 'json',
                    success: function(result) {
                        augmented.innerHTML = "Augmentation terminated";
                        var converted = document.createElement("li");
                        converted.innerHTML = "Converting boxes in tfRecords...";
                        list.append(converted);

                        $.ajax({
                            type: "POST",
                            async: true,
                            url: "/convert-annotations",
                            data: JSON.stringify(datasetName),
                            contentType: "application/json",
                            dataType: 'json',
                            success: function(result) {
                                converted.innerHTML = "Boxes correctly coverted in tfRecords";
                                var trained = document.createElement("li");
                                trained.innerHTML = "Training started...";
                                var p = document.createElement("p");
                                p.innerHTML = "You can monitor training with ";
                                var link = document.createElement("a");
                                link.setAttribute("href", "http://localhost:6006/");
                                link.setAttribute("target", "_blank");
                                link.innerHTML = "tensorBoard";
                                p.append(link);
                                trained.append(p);
                                list.append(trained);

                                $.ajax({
                                    type: "POST",
                                    async: true,
                                    url: "/train",
                                    data: JSON.stringify(server_data),
                                    contentType: "application/json",
                                    dataType: 'json',
                                    success: function(result) {
                                        converted.innerHTML = "Training terminated";
                                    }
                                })
                            }
                        })
                    }
                })
            }
        })
    }
}
