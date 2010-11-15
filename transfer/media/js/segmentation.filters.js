(function ($) {
    $(window).load(function () {
        initialize();
    });

    initialize = function () {
        var jsonRegions, region, imgImage, canvas, context;
        jsonRegions = $.parseJSON($("#id_regions").val());
        canvas = document.getElementById("canvasImageToProcess");
        context = canvas.getContext("2d");
        imgImage = document.getElementById("imageToProcess");
        context.drawImage(imgImage, 0, 0);
        for(var i in jsonRegions) {
            region = jsonRegions[i];
            context.strokeStyle = "#0000FF";
            context.strokeRect(region.box[0], region.box[1], region.box[2], region.box[3]);
        }
    }

})(jQuery.noConflict());
