(function ($) {
    $(window).load(function () {
        initialize();
    });

    $('#canvasImageToProcess').mousewheel(function(event, delta, deltaX, deltaY) {
        var value;
        if (delta > 0) {
            value = parseFloat($("#slider").slider("value")) + 0.01;
        } else {
            value = parseFloat($("#slider").slider("value")) + 0.01;
        }
        $("#slider").slider("value", value);
    });

    initialize = function () {
        var canvas, context, imgOriginal, imgMask, startScale, scale, intervalId, imageData, copiedCanvas, xLast, yLast, portal, scaleString, previousX, previousY, mouseIsDown, performingZoom;
        scale = 0.25;
        canvas = document.getElementById("canvasImageToProcess");
        context = canvas.getContext("2d");
        width = context.canvas.width;
        height = context.canvas.height;
        imgOriginal = document.getElementById("originalImage");
        imgMask = document.getElementById("maskImage");
        drawOverlay = function(canvas, img, mask, scale) {
            canvas.width = canvas.width;
            ctx = canvas.getContext("2d");
            ctx.save();
            ctx.scale(scale, scale);
            ctx.drawImage(imgOriginal, 0, 0);
            ctx.drawImage(imgOriginal, imgOriginal.width, 0);
            ctx.globalCompositeOperation = 'lighter';
            ctx.drawImage(imgMask, imgOriginal.width, 0);
            ctx.restore();
        }
        drawOverlay(canvas, imgOriginal, imgMask, scale);

         $("#scale" ).slider({
            value: 0.25,
            min: 0,
            max: 1,
            step: 0.01,
            change: function(event, ui) {
                var imgOriginal, imgMask;
                imgOriginal = document.getElementById("originalImage");
                imgMask = document.getElementById("maskImage");
                drawOverlay(canvas, imgOriginal, imgMask, ui.value);
            }
        });

        // Based on http://www.dominicpettifer.co.uk/Files/MosaicZoom.html
        performingZoom = false;
        mouseIsDown = false;
        previousX = 0;
        previousY = 0;
        xLast = 0;
        yLast = 0;
        portal = {
            width: 800,
            height: 600,
            x: 0,
            y: 0,
            scale: 1,
            mouseX: 0,
            mouseY: 0,
            element: $('#imageViewer > div')
        };
        $('#imageViewer > div').css('-moz-transform-origin', '0px 0px')
            .css('-webkit-transform-origin', '0px 0px')
            .css('-o-transform-origin', '0px 0px');
        $("#imageViewer").mousedown(function () {
            mouseIsDown = true;
            return false;
        });
        $("#imageViewer").mouseup(function (e) {
            mouseIsDown = false;
            return false;
        });
        $("#imageViewer").mousemove(function (e) {
            var xScreen, yScreen, percentageX, percentageY, virtualX, virtualY, originX, originY;
            xScreen = e.pageX - $(this).offset().left;
            yScreen = e.pageY - $(this).offset().top;
            if (mouseIsDown) {
                percentageX = (100 / 800) * xScreen;
                percentageY = (100 / 600) * yScreen;
                virtualX = ((portal.Width / 100) * percentageX);
                virtualY = ((portal.height / 100) * percentageY);
                originX = virtualX + portal.x;
                originY = virtualY + portal.y;
                portal.mouseX = originX;
                portal.mouseY = originY;
                if (xScreen > previousX) {
                    portal.x -= (xScreen - previousX) / scale;
                } else {
                    portal.x += (previousX - xScreen) / scale;
                }
                if (yScreen > previousY) {
                    portal.y -= (yScreen - previousY) / scale;
                } else {
                    portal.y += (previousY - yScreen) / scale;
                }
                $('#zoomPortal > div.outline')
                    .height(portal.height / 10)
                    .width(portal.width / 10)
                    .css('left', portal.x / 10 + 'px')
                    .css('top', portal.y / 10 + 'px');
                $('#zoomPortal > div.mouse')
                    .css('left', portal.mouseX / 10 + 'px')
                    .css('top', portal.mouseY / 10 + 'px');
                scaleString = 'translate(-' + portal.x + 'px, -' + portal.y + 'px' + ')';
                portal.element
                    .css('-moz-transform', scaleString)
                    .css('-webkit-transform', scaleString)
                    .css('-o-transform', scaleString);
            }
            previousX = xScreen;
            previousY = yScreen;
        });

        imageMouseWheel = function (e, delta) {
            var xScreen, yScreen, scaleFrom, scaleIncrement;
            if (!performingZoom) {
                performingZoom = true;
                // Find current location on screen 
                xScreen = e.pageX - $(this).offset().left;
                yScreen = e.pageY - $(this).offset().top;
                scaleFrom = scale;
                // Determine the new scale
                if (delta > 0) {
                    scale *= 2;
                } else {
                    scale /= 2;
                }
                scale = scale < 1 ? 1 : (scale > 64 ? 64 : scale);
                if (scale == 1) {
                    portal.mouseX = 0;
                    portal.mouseY = 0;
                    xLast = 0;
                    yLast = 0;
                }
                scaleIncrement = (scale - scaleFrom) / 5;
                console.log(scale/64)
                animationZoomOut(xScreen, yScreen, $(this).find('div'), scaleFrom, scaleIncrement, scale);
            }
            return false;
        };
        $("#imageViewer").mousewheel();

        function animationZoomOut(xScreen, yScreen, element, scaleFrom, scaleIncrement, endScale) {
            var scaleTo, xNew, yNew, percentageX, percentageY, originX, originY;
            // Find current location on the image at the current scale
            portal.mouseX = portal.mouseX + ((xScreen - xLast) / scaleFrom);
            portal.mouseY = portal.mouseY + ((yScreen - yLast) / scaleFrom);
            scaleTo = scaleFrom + scaleIncrement;
            scaleTo = scaleTo > endScale ? endScale : scaleTo;
            // Determine the location on the screen at the new scale
            xNew = (xScreen - portal.mouseX) / scaleTo;
            yNew = (yScreen - portal.mouseY) / scaleTo;
            if (scaleTo == 1) {
                xNew = 0;
                yNew = 0;
            }
            portal.scale = scaleTo;
            portal.width = 800 / scaleTo;
            portal.height = 600 / scaleTo;
            portal.x = (portal.mouseX - (portal.mouseX / scaleTo)) - xNew;
            portal.y = (portal.mouseY - (portal.mouseY / scaleTo)) - yNew;
            // Save the current screen location
            xLast = xScreen;
            yLast = yScreen;

            $('#zoomPortal > div.outline').height(portal.height/10).width(portal.width/10).css('left', portal.x/10 + 'px').css('top', portal.y/10 + 'px');
            percentageX = (100 / 800) * xScreen;
            percentageY = (100 / 600) * yScreen;
            originX = ((portal.width / 100) * percentageX) + portal.x;
            originY = ((portal.height / 100) * percentageY) + portal.y;
            $('#zoomPortal > div.mouse')
                .css('left', originX / 10 + 'px')
                .css('top', originY / 10 + 'px');
            scaleString = 'scale(' + scaleTo + ') translate(-' + portal.x + 'px, -' + portal.y + 'px)';
            element
                .css('-moz-transform', scaleString)
                .css('-webkit-transform', scaleString)
                .css('-o-transform', scaleString);
            if (scaleTo < endScale) {
                setTimeout(function () {
                    animationZoomOut(xScreen, yScreen, element, scaleTo, scaleIncrement, endScale);
                }, 20);
            } else {
                performingZoom = false;
                if (portal.scale == 8) {
                    // TODO: Put here the code to translate and scale canvas
                }
            }
        }
    }
})(jQuery.noConflict());
