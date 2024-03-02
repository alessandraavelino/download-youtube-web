setTimeout(function(){
    console.log("ok")
    let alert = document.getElementById("alert")
    if (alert) {
        alert.style.display = "none"
    }
}, 3000);

console.log("oi")