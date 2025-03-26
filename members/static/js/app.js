console.log("app.js a été chargé"); //Savoir si le app.js a été appelé

//Afficher le menu de navigation
menubar = document.querySelector('.menu-btn');
menuslide = document.querySelector('.menu-slide');
menubar.addEventListener("click", ()=>{
    menuslide.classList.toggle("menu_active");
    menubar.classList.toggle("x_active");
    console.log("ok");
});

//Afficher le chatbot en bas à droite
chat_section = document.getElementById('chat-section')
bouton_nova = document.getElementById('nova-bouton')
bouton_nova.addEventListener('click', ()=>{
    chat_section.classList.toggle('bot_visibilité')
});
// Cacher le chatbot si on clique à l'extérieur
document.addEventListener('click', (event) => {
    if (!chat_section.contains(event.target) && !bouton_nova.contains(event.target)) {
        chat_section.classList.remove('bot_visibilité'); // Cache le chatbot
    }
});


//Discuter avec le chatbot
function envoyerMessage(){
    /*Zone du chat*/
    chat_box = document.getElementById('chat-box')

    /*Message de l'utilisateur et du bot*/
    message_element_utilisateur = document.createElement("h2")
    message_element_utilisateur.classList.add("user-message")
    message_element_bot = document.createElement("h2")
    message_element_bot.classList.add("bot-message")
    /*Message d'erreur*/
    message_element_erreur = document.createElement("h2")
    message_element_erreur.innerHTML = "Erreur"
     /*Envoyer le message de l'utilisateur dans la zone de chat*/
    message_utilisateur = document.getElementById('user-input').value
    if (message_utilisateur.trim() ==='') return;

    message_element_utilisateur.innerHTML = message_utilisateur
    chat_box.appendChild(message_element_utilisateur)
    document.getElementById('user-input').value = ""

    /*Envoyer la réponse du bot dans la zone de chat*/
    $.ajax({
        type: 'POST',
        url: '/tableau-bord/reponseBot',
        data: {message: message_utilisateur, csrfmiddlewaretoken: '{{ csrf_token }}'},
        success: function (reponse){
            message_element_bot.innerHTML = reponse.response
            chat_box.appendChild(message_element_bot)
        },
        error: function (){
            chat_box.appendChild(message_element_erreur)
        }
    })
    scrollToBottom()

}
function scrollToBottom() {
    let chatBox = document.getElementById("chat-box");
    setTimeout(() => {
        chatBox.scrollTo({
          top: chatBox.scrollHeight,
          behavior: "smooth"
        });
    }, 100);
}
function enter(){
    document.getElementById("user-input").addEventListener("keyup", function(event) {
        event.preventDefault();
        if (event.keyCode === 13) {
            document.getElementById("envoyer-message").click();
        }
    });
}

function getValue(selector) {
    let element = document.querySelector(selector);
    return element ? parseFloat(element.value) || 0 : 0;
}

function calculerCapital() {

    console.log("📊 calculerCapital() a été appelée !"); //Pour savoir si la fonction est appelée

    let actifs = [
        getValue(".cheque"),
        getValue(".epargne"),
        getValue(".bourse"),
        getValue(".crypto"),
        getValue(".autre")
    ];
    let passifs = [
        getValue(".credits"),
        getValue(".emprunts"),
        getValue(".hypotheque")
    ];

    let totalActifs = actifs.reduce((acc, val) => acc + val, 0);
    let totalPassifs = passifs.reduce((acc, val) => acc + val, 0);
    let capital = totalActifs - totalPassifs;

    document.getElementById("capital-value").textContent = capital.toLocaleString() + " $";

    console.log("Valeur chèque :", getValue(".cheque"));
    console.log("Valeur épargne :", getValue(".epargne"));
    console.log("Valeur bourse :", getValue(".bourse"));
    console.log("Valeur crypto :", getValue(".crypto"));
    console.log("Valeur autre :", getValue(".autre"));

    console.log("Valeur crédits :", getValue(".credits"));
    console.log("Valeur emprunts :", getValue(".emprunts"));
    console.log("Valeur hypothèque :", getValue(".hypotheque"));
}

document.addEventListener("DOMContentLoaded", function () {
    let boutonCalcul = document.querySelector(".calculer");
    if (boutonCalcul) {
        boutonCalcul.addEventListener("click", calculerCapital());
    } else {
        console.error("Le bouton de calcul n'a pas été trouvé !"); //Test de debug
    }
});


