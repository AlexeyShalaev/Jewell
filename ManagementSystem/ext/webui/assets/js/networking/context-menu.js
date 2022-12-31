let events = ["contextmenu", "click"];
let contextMenu = document.getElementById("context-menu");
var showMenu = function (e) {
    e.preventDefault();
    //x and y position of mouse or touch
    let mouseX = e.clientX || e.center.x || e.touches[0].clientX;
    let mouseY = e.clientY || e.center.y || e.touches[0].clientY;
    //height and width of menu
    let menuHeight = contextMenu.getBoundingClientRect().height;
    let menuWidth = contextMenu.getBoundingClientRect().width;
    //width and height of screen
    let width = window.innerWidth;
    let height = window.innerHeight;
    //If user clicks/touches near right corner
    if (width - mouseX <= 200) {
        contextMenu.style.borderRadius = "5px 0 5px 5px";
        contextMenu.style.left = width - menuWidth + "px";
        contextMenu.style.top = mouseY + "px";
        //right bottom
        if (height - mouseY <= 200) {
            contextMenu.style.top = mouseY - menuHeight + "px";
            contextMenu.style.borderRadius = "5px 5px 0 5px";
        }
    }
    //left
    else {
        contextMenu.style.borderRadius = "0 5px 5px 5px";
        contextMenu.style.left = mouseX + "px";
        contextMenu.style.top = mouseY + "px";
        //left bottom
        if (height - mouseY <= 200) {
            contextMenu.style.top = mouseY - menuHeight + "px";
            contextMenu.style.borderRadius = "5px 5px 5px 0";
        }
    }
    //display the menu
    contextMenu.style.visibility = "visible";
};
