(function($) {
    $(document).ready(function() {

        initialize = function() {
            $("#id_method").change(function() {
                var value;
                value = $(this).val();
                if (value) {
                    $(".button").show();
                    $.ajax({
                        url: '/methods/form/'+ value,
                        success: function(data) {
                            $('#id_fieldset').html(data);
                        }
                    });
                } else {
                    $(".button").hide();
                }
            });

            $("#id_preview").click(function() {
                $("#id_preview_value").val("true");
                $("#id_method_form").submit();
            });

            $("#id_custom").click(function() {
                $("#id_fieldset").toggle();
            });
        };

        initialize();
    });
})(jQuery.noConflict());
