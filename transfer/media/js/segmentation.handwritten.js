(function ($) {
    $(window).load(function () {
        initialize();
    });

    initialize = function () {
        var jsonRegions, region, imgImage, canvas, context, color;
        canvas = document.getElementById("canvasImageToProcess");
        context = canvas.getContext("2d");
        imgImage = document.getElementById("imageToProcess");
        context.drawImage(imgImage, 0, 0);
    }

})(jQuery.noConflict());
