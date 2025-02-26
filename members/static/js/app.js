menubar = document.querySelector('.menu-btn');
menuslide = document.querySelector('.menu-slide');
menubar.addEventListener("click", ()=>{
    menuslide.classList.toggle("menu_active");
    menubar.classList.toggle("x_active");
});
