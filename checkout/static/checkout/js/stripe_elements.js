/*
    This is to create and enable the stripe smart checkout.
    Used https://stripe.com/docs/payments/accept-a-payment
    to create functionality of the payment methods.
    This file sets up the payments and transactions of my site
    it uses stripe features to create and take payments.
*/
var stripePublicKey = $("#id_stripe_public_key").text().slice(1, -1);
var clientKey = $('#id_client_secret').text().slice(1, -1);
var stripe = Stripe(stripePublicKey);
var elements = stripe.elements();

var style = {
    base: {
        fontFamily: '"Segoe UI", sans-serif',
        color: "blue",
    },
    invalid: {
        color: "red",
    }
};

var card = elements.create("card", {
    style: style
});

card.mount("#card-element");

card.addEventListener("change", function(event) {
    var errorC = document.getElementById("card-errors");
    if (event.error) {
        var html = `
        <span> ${ event.error.message } </span>
        `;
        errorC.innerHTML = html;
    } else {
        errorC.innerHTML = "";
    }
});
