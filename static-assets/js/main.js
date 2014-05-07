/********* Common *********/

function convert_to_jalali(date, format) {
	if (date == null || date == '') {
		return '';
	}	
	format = format || 'yy/mm/dd';
	return $.datepicker.formatDate(format, new JalaliDate(new Date(date)))
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
		$(this).find("h3").addClass("alert alert-info");
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
				dateFormat: 'yy/mm/dd'
			}); 
		}
	});
	
	$(".convert-date").each(function() {
		if (!$(this).hasClass("converted")) {
			$(this).addClass("converted").text(convert_to_jalali($(this).text()));
		}
	});
	
	$("[data-role=chosen]:visible").livequery(function() {
		$(this).addClass("chosen-rtl").chosen({
			placeholder_text: "انتخاب کنید...",
			no_results_text: "هیچ گزینه ای یافت نشد مطابق"
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
    $('a[data-confirm]').livequery(function() {
        $(this).click(function(ev) {
            var href = $(this).attr('href');

            if (!$('#dataConfirmModal').length) {
                $('body').append('<div id="dataConfirmModal" class="modal" role="dialog" aria-labelledby="dataConfirmLabel" aria-hidden="true"><div class="modal-header"><button type="button" class="close" data-dismiss="modal" aria-hidden="true">�</button><h3 id="dataConfirmLabel">Please Confirm</h3></div><div class="modal-body"></div><div class="modal-footer"><button class="btn btn-default" data-dismiss="modal" aria-hidden="true">Cancel</button><a class="btn btn-primary" id="dataConfirmOK">OK</a></div></div>');
            } 
            $('#dataConfirmModal').find('.modal-body').text($(this).attr('data-confirm'));
            $('#dataConfirmOK').attr('href', href);
            $('#dataConfirmModal').modal({show:true});
            return false;
        });
    });
});