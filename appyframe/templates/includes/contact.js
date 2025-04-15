// Copyright (c) 2015, Appyframe Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

appyframe.ready(function() {

	if(appyframe.utils.get_url_arg('subject')) {
	  $('[name="subject"]').val(appyframe.utils.get_url_arg('subject'));
	}

	$('.btn-send').off("click").on("click", function() {
		var email = $('[name="email"]').val();
		var message = $('[name="message"]').val();

		if(!(email && message)) {
			appyframe.msgprint('{{ _("Please enter both your email and message so that we can get back to you. Thanks!") }}');
			return false;
		}

		if(!validate_email(email)) {
			appyframe.msgprint('{{ _("You seem to have written your name instead of your email. Please enter a valid email address so that we can get back.") }}');
			$('[name="email"]').focus();
			return false;
		}

		$("#contact-alert").toggle(false);
		appyframe.call({
			type: "POST",
			method: "appyframe.www.contact.send_message",
			args: {
				subject: $('[name="subject"]').val(),
				sender: email,
				message: message,
			},
			callback: function(r) {
				if (!r.exc) {
					appyframe.msgprint('{{ _("Thank you for your message") }}', '{{ _("Message Sent") }}');
				}
				$(':input').val('');
			},
		});
	});
});

var msgprint = function(txt) {
	if(txt) $("#contact-alert").html(txt).toggle(true);
}
