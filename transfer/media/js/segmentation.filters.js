(function ($) {
    $(window).load(function () {
        initialize();
    });

    initialize = function () {
        var jsonRegions, region, imgImage, canvas, context, color;
        jsonTypesRegions = $.parseJSON($("#id_regions").val());
        canvas = document.getElementById("canvasImageToProcess");
        context = canvas.getContext("2d");
        imgImage = document.getElementById("imageToProcess");
        context.drawImage(imgImage, 0, 0);
        for(var i in jsonTypesRegions) {
            if (i == 0) {
                color = "#00FF00";
            } else if (i == 1) {
                color = "#0000FF";
            } else {
                color = "#FF0000";
            }
            for(var j in jsonTypesRegions[i]) {
                region = jsonTypesRegions[i][j];
                context.strokeStyle = color;
                context.strokeRect(region.box[0], region.box[1], region.box[2], region.box[3]);
            }
        }
    }

})(jQuery.noConflict());
