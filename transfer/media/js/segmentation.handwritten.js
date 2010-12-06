(function ($) {
    $(window).load(function () {
        initialize();
    });

    initialize = function () {
        var canvas, context, imgOriginal, imgMask;
        canvas = document.getElementById("canvasImageToProcess");
        context = canvas.getContext("2d");
        imgOriginal = document.getElementById("originalImage");
        imgMask = document.getElementById("maskImage");
        context.scale(0.25, 0.25);
        context.drawImage(imgOriginal, 0, 0);
        context.globalCompositeOperation = 'darker';
        context.drawImage(imgMask, 0, 0);
    }

})(jQuery.noConflict());
