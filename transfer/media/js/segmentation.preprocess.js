(function ($) {
    $(document).ready(function () {
        initialize();
        $("#id_invert_apply").click(function () {
            var image;
            image = document.getElementById("imageToProcess");
            Pixastic.process(image, "invert");
        });

        $("#id_threshold_apply").click(function () {
            var image, value;
            image = document.getElementById("imageToProcess");
            Pixastic.revert(image);
            value = parseInt($("#id_threshold").val()) || 128;
            if (value == NaN || value > 255) {
                value = 128;
            }
            $("#id_threshold").val(value);
            Pixastic.process(image, "binarization", {'threshold': value});
        });

        $("#preprocessForm").submit(function() {
            var canvas, dataURL;
            canvas = document.getElementById("imageToProcess");
            dataURL = canvas.toDataURL("image/png");
            $("#id_base64_image").val(dataURL);
            console.log(dataURL);
            return true;
        });

    });

    initialize = function () {
        $("#id_threshold_apply").click();
    }

})(jQuery.noConflict());
