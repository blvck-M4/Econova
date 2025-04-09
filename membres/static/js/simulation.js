// Sélectionne tous les éléments ayant la classe 'symbols'
        symbols = document.querySelectorAll('.symbols');

        // Récupère les éléments du popup
        produit_info = document.getElementById('produit-info');
        popupTitle = document.getElementById('produit-titre');
        popupTendance = document.getElementById('produit-tendance');
        popupRisque = document.getElementById('produit-risque');
        popupType = document.getElementById('produit-type');
        produit_fermer = document.getElementById('fermer-produit');

// Fermer le popup lorsque l'utilisateur clique sur "X"
produit_fermer.addEventListener('click', () => {
    produit_info.style.display = "none";
});

// Fermer le popup si l'utilisateur clique en dehors du contenu
produit_info.addEventListener('click', (event) => {
    if (event.target === produit_info) {
        produit_info.style.display = "none";
    }
});


ouvrir_historique = document.querySelector('.ouvrir-historique')
historique = document.getElementById('historique')
ouvrir_historique.addEventListener('click',()=>{
    historique.classList.toggle('historique-visible')
})
fermer_historique = document.querySelector('.fermer-historique')
fermer_historique.addEventListener('click', ()=>{
    if (historique.classList.contains('historique-visible')){
        historique.classList.remove('historique-visible')
    }
})




bouton_produit = document.querySelectorAll('.type-produit div')
actions_tableau = document.querySelector('.actions-tableau')
tableau_produit = document.querySelectorAll('.tableau-produit tbody')
bouton_produit.forEach((produit)=>{
    produit.addEventListener('click', ()=>{
        produit.classList.toggle('produit-select');
        // Liste des autres boutons à désélectionner
        let autresBoutons = Array.from(bouton_produit).filter(btn => btn !== produit);

        // Retirer la classe 'produit-select' des autres boutons
        autresBoutons.forEach(btn => btn.classList.remove('produit-select'));

        tableau_produit.forEach((tableau) => {
            let idCorrespondant = produit.id.replace('bouton', 'tab');

            if (tableau.id === idCorrespondant) {
                tableau.classList.toggle('tableau-visible');
            } else {
                tableau.classList.add('tableau-visible');
            }
        });
    })
})