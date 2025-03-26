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

//Calculer le capital

function calculerCapital() {
    let actifs = [
        parseFloat(document.getElementById("cheque").value) || 0,
        parseFloat(document.getElementById("epargne").value) || 0,
        parseFloat(document.getElementById("bourse").value) || 0,
        parseFloat(document.getElementById("crypto").value) || 0,
        parseFloat(document.getElementById("autre").value) || 0,
    ];
    let passifs = [
        parseFloat(document.getElementById("credits").value) || 0,
        parseFloat(document.getElementById("emprunts").value) || 0,
        parseFloat(document.getElementById("hypotheque").value) || 0,
    ];

    let totalActifs = actifs.reduce((acc, val) => acc + val, 0);
    let totalPassifs = passifs.reduce((acc, val) => acc + val, 0);
    let capital = totalActifs - totalPassifs;

    document.getElementById("capital-value").textContent = capital.toLocaleString() + " $";
}

// Appeler cette fonction après la saisie des montants

document.addEventListener("DOMContentLoaded", function () {
    // Sélectionne le bouton avec la classe "calculer"
    document.querySelector(".calculer").addEventListener("click", calculerCapital);
});

console.log(document.querySelector(".calculer"));


