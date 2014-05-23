/********* Common *********/

function convert_to_jalali(date, format) {
	if (date == null || $.trim(date) == '' || $.trim(date) == 'None') {
		return '';
	}	
	format = format || 'yy/mm/dd';
	return $.datepicker.formatDate(format, new JalaliDate(new Date(date)));
}

function select_items_for_dropdown(dropdown_selector, items) {
	dropdown = $(dropdown_selector);
	$.each(items, function(i, v) {	
		dropdown.find("option[value=" + v + "]").attr("selected", "selected");		
	});
	if (dropdown.hasClass("chosen") || dropdown.hasClass("chosen-rtl")) {
		dropdown.trigger("chosen:updated");
	}
}

$(document).ready(function() {
	var link_id = ($("#top-nav-links").data("active-link-id") || "home") + "-link";
	$("li#" + link_id).addClass("active");
	
	$('ul.nav a[href="' + window.location.hash + '"]').tab('show');
	
	$(".required-field").livequery(function() {
		var label = $(this);
		label.parent().find(":input").attr("required", "required");
		if (!label.hasClass("required")) {
			label.addClass("required").append('<span class="icon-required" title="این فیلد الزامی است"></span>');
		}
	});
	
	$(".modal-header").livequery(function() {
		var h3 = $(this).find("h3")
		if (h3.hasClass("confirm-delete")) {
			h3.addClass("alert alert-warning");
		}
		else {
			h3.addClass("alert alert-info");
		}
	});
		
	$(".form-horizontal .form-group > div").livequery(function() {
		$(this).addClass("col-lg-10");
	});
	$(".form-horizontal .form-group > label").livequery(function() {
		$(this).addClass("col-lg-2");
	});
	$("[data-role=calendar]:visible").livequery(function() {
		if (!$(this).hasClass("converted") && !$(this).attr("data-ignore-convert")) {
			$(this).addClass("converted").val(convert_to_jalali($(this).val()));		
			$(this).datepicker({
				changeMonth: true,
				changeYear: true,
				dateFormat: 'yy/mm/dd',
				yearRange: '1350:1450'
			}); 
		}
	});
	
	$(".convert-date").livequery(function() {
		if (!$(this).hasClass("converted")) {
			$(this).addClass("converted").text(convert_to_jalali($(this).text(), $(this).data("date-format")));
		}
	});
	
	$("[data-role=chosen]:visible").livequery(function() {
		$(this).addClass("chosen-rtl").chosen({
			placeholder_text: $(this).attr("placeholder") || "انتخاب کنید...",
			no_results_text: "هیچ گزینه ای یافت نشد مطابق",
			width: $(this).attr("data-width")? $(this).attr("data-width") + "!important": "100%"
		});
	})
	$("[data-role=chosen]:visible").livequery(function() {
		$(this).chosen({ allow_single_deselect: true });
	});

	$(":file:visible").livequery(function() {
		$(this).filestyle({
			classInput: "right-space",
			buttonText: "انتخاب فایل",
			buttonBefore: true,
			classIcon: "glyphicon glyphicon-file"
		});	
	});
	$(".bootstrap-filestyle input").livequery(function() {
		$(this).addClass("form-control");
	});
	
	$("[data-role=wysihtml5]:visible").attr("dir", "rtl").wysihtml5({
		image: false,
		color: true,
		html: true
	});
	$(".wysihtml5-toolbar a.dropdown-toggle").attr('tabindex', '-1');
	
	$("[title]").livequery(function() {
		if (!$(this).closest("[data-disable-powertip=true]").length) {
			$(this).powerTip({smartPlacement: true, placement: $(this).data("placement") || $(this).closest("[data-powertip-parent=true]").data("placement") || "n"});
		}
	});
	
	$('.dropdown').on('show.bs.dropdown', function(e) {
		$(this).find('.dropdown-menu').first().stop(true, true).slideDown('fast');
	});

	$('.dropdown').on('hide.bs.dropdown', function(e) {
		$(this).find('.dropdown-menu').first().stop(true, true).slideUp('fast');
	});
});

/********* Modal *********/

$(document).ready(function() {
    $.modalPanel = $("#app-modal");
});

function modal_form_keypress(event) {
    if (event.which == 13 || event.keyCode == 13) {
        $.modalPanel.find("form").submit();
        return false;
    }
    return true;
}

function modal_form_submit() {
    $.modalPanel.css("cursor", "wait");
    $.post($(this).attr("action"), $(this).serialize(), function(data) { 
        try {
            $.modalPanel.html(data); 
            $.modalPanel.find("form").submit(modal_form_submit);
            $.modalPanel.find("form .controls input").first().focus();
            $.modalPanel.css("cursor", "default");
        } catch(err) {
        }
    });
    return false;    
}

$(document).ready(function() {
    $("[data-toggle=modal]").livequery(function() {
        $(this).on("click", function(e) {
            e.preventDefault();
            $("body").modalmanager("loading");     
            $.modalPanel.empty();
            $.modalPanel.load($(this).attr("href") || $(this).data("target"), "", function() {
                $.modalPanel.modal({ backdrop: "static" });
                $.modalPanel.find("form").submit(modal_form_submit);
                $.modalPanel.find("form input").keypress(modal_form_keypress);
            });
            return false;
        });
    });
});

/********* Confirm Dialog *********/

$(document).ready(function() {
    $('[data-confirm]').livequery(function() {
        $(this).click(function(ev) {
            var href = $(this).attr('href');
			var _this = $(this);

            if (!$('#dataConfirmModal').length) {
                $('body').append('<div id="dataConfirmModal" class="modal fade" role="dialog" aria-labelledby="dataConfirmLabel" aria-hidden="true"><div class="modal-header"><h3 id="dataConfirmLabel" class="confirm-delete">لطفا تایید کنید</h3></div><div class="modal-body"></div><div class="modal-footer"><button class="btn btn-default" data-dismiss="modal" aria-hidden="true">خیر</button><a class="btn btn-danger" id="dataConfirmOK">بله</a></div></div>');
            } 
            $('#dataConfirmModal').find('.modal-body').text($(this).attr('data-confirm'));
			if ($(this).is("a")) {
				$('#dataConfirmOK').attr('href', href);
			}
			else {
				$('#dataConfirmOK').click(function () {
					$(_this).closest("form").submit();
				});
			}
            $('#dataConfirmModal').modal({show:true});
            return false;
        });
    });
});

/********* Ajax Loader *********/

function ajaxIndicatorStart(img, text) {
	if(jQuery('body').find('#resultLoading').attr('id') != 'resultLoading') {
		jQuery('body').append('<div id="resultLoading" style="display:none"><div><img src="' + img + '"><div>'+text+'</div></div><div class="bg"></div></div>');
	}
	
	jQuery('#resultLoading').css({
		'width':'100%',
		'height':'100%',
		'position':'fixed',
		'z-index':'10000000',
		'top':'0',
		'left':'0',
		'right':'0',
		'bottom':'0',
		'margin':'auto'
	});	
	
	jQuery('#resultLoading .bg').css({
		'background':'#000000',
		'opacity':'0.7',
		'width':'100%',
		'height':'100%',
		'position':'absolute',
		'top':'0'
	});
	
	jQuery('#resultLoading>div:first').css({
		'width': '250px',
		'height':'75px',
		'text-align': 'center',
		'position': 'fixed',
		'top':'0',
		'left':'0',
		'right':'0',
		'bottom':'0',
		'margin':'auto',
		'font-size':'16px',
		'z-index':'10',
		'color':'#ffffff'
		
	});

	jQuery('#resultLoading .bg').height('100%');
	jQuery('#resultLoading').fadeIn(300);
	jQuery('body').css('cursor', 'wait');
}

function ajaxIndicatorStop() {
	jQuery('#resultLoading .bg').height('100%');
	jQuery('#resultLoading').fadeOut(300);
	jQuery('body').css('cursor', 'default');
}