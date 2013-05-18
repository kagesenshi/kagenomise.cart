/* script.js */

$(document).ready(function () {
    simpleCart.currency({
        code: 'MYR',
        name: 'Malaysian Ringgit',
        symbol: 'MYR'
    });
    simpleCart({
        checkout: {
            type: 'SendForm',
            url: $('#kagenomise-cartmetadata').attr('checkout-url')
        },
        cartStyle: 'table',
        currency: 'MYR',
            cartColumns: [
                { attr: "name" , label: "Name" } ,
                { attr: "size" , label: "Size" } ,
                { attr: "price" , label: "Price", view: 'currency' } ,
                { view: "decrement" , label: false , text: "-" } ,
                { attr: "quantity" , label: "Qty" } ,
                { view: "increment" , label: false , text: "+" } ,
                { attr: "total" , label: "SubTotal", view: 'currency' } ,
                { view: "remove" , text: "Remove" , label: false }
        ]
    })

    $(".cartInfo").toggle(function(){
        $("#cartPopover").show();
        $(".cartInfo").addClass('open');
    }, function(){
        $("#cartPopover").hide();
        $(".cartInfo").removeClass('open');
    });
});
