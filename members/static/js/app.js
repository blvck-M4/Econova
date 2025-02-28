menubar = document.querySelector('.menu-btn');
menuslide = document.querySelector('.menu-slide');
menubar.addEventListener("click", ()=>{
    menuslide.classList.toggle("menu_active");
    menubar.classList.toggle("x_active");
});


suivant = document.querySelector('.suivant');
question = document.querySelectorAll('.question');
var i = 0;
suivant.addEventListener("click", ()=>{
    if(i < question.length-1){
        question[i].classList.toggle("visible");
        i++;
        question[i].classList.toggle("visible");
    }
})

retour = document.querySelector('.retour');
retour.addEventListener('click', ()=>{
    if(i > 0){
        question[i].classList.toggle("visible");
        i--;
        question[i].classList.toggle("visible");
    }
})


