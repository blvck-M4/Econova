//Afficher les onglets des outils financiers
onglet_outils = document.querySelector('.onglet-outils');
outils = document.querySelector('.outils');
triangle = document.querySelector('.triangle');
onglet_outils.addEventListener('click', ()=>{
    outils.classList.toggle("visible");
    triangle.classList.toggle("rotate");
});

//Afficher le menu du profil
icon_profile = document.querySelector('.icon-profile');
menu_profil = document.querySelector('.menu-profil');

icon_profile.addEventListener('click', ()=>{
    menu_profil.classList.toggle("menu-hide");
});

document.addEventListener('click', e=>{
    if(!menu_profil.contains(e.target) && icon_profile != e.target){
        menu_profil.classList.add("menu-hide");
    }
});

//Dans la page profil, afficher la page pour modifier l'information sélectionné
document.addEventListener("DOMContentLoaded", () => {
    const input1 = document.getElementById('input1');
    const input2 = document.getElementById('input2');
    const input3 = document.getElementById('input3');
    const input4 = document.getElementById('input4');
    const input5 = document.getElementById('input5');
    const input6 = document.getElementById('input6');


    const utilisateur = document.getElementById('utilisateur');
    const nom = document.getElementById('nom');
    const email = document.getElementById('email');
    const motDePasse = document.getElementById('motdepasse');
    const date_naissance = document.getElementById('date-naissance');
    const genre = document.getElementById('genre');
    const formModifier = document.querySelector('.form-modifier');
    const annuler = document.querySelector('.annuler'); // Bouton pour fermer

    const inputs = [input1, input2, input3, input4, input5, input6];
    const headers = [utilisateur, nom, email, motDePasse, date_naissance, genre];

    headers.forEach((header, index) => {
        header.addEventListener("click", () => {
            formModifier.classList.remove("form-hide");

            // Masquer tous les inputs sauf celui correspondant au h3 cliqué
            inputs.forEach((input, i) => {
                input.classList.toggle("input-hide", i !== index);
            });
        });
    });

    // Gérer le bouton "Annuler"
    annuler.addEventListener("click", () => {
        formModifier.classList.add("form-hide"); // Cache le formulaire

        // Masquer tous les champs input
        inputs.forEach(input => input.classList.add("input-hide"));
    });
});

