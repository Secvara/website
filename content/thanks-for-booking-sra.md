---
title: "Thanks for Booking Your SRA"
description: "Confirmation landing page for Security Risk Assessment booking."
---

# Thanks for booking your SRA

We received your Security Risk Assessment request and will be in touch with next steps. If you have any immediate questions, email [hello@secvara.com](mailto:hello@secvara.com).

<div id="booking-details"></div>

<!-- Data layer event for Book appointment conversion page -->
<script>
  (function () {
    window.dataLayer = window.dataLayer || [];

    const params = new URLSearchParams(window.location.search);
    const readParam = (key) => {
      const value = params.get(key);
      return value && value.trim() ? value.trim() : null;
    };

    const bookingDetails = {};
    const assignDetail = (field, key) => {
      const value = readParam(key);
      if (value) {
        bookingDetails[field] = value;
      }
      return value;
    };

    const name = assignDetail('name', 'name');
    const email = assignDetail('email', 'email');
    const eventType = assignDetail('eventType', 'eventTypeName') || assignDetail('eventType', 'eventTypeSlug');
    const timeZone = assignDetail('timeZone', 'timeZone');
    const meetingUrl = assignDetail('meetingUrl', 'meetingUrl') || assignDetail('meetingUrl', 'conferenceUrl');
    const location = assignDetail('location', 'location');
    const rescheduleLink = assignDetail('rescheduleLink', 'rescheduleLink');
    const cancelLink = assignDetail('cancelLink', 'cancelLink');

    const startTimeRaw = readParam('startTime');
    if (startTimeRaw) {
      bookingDetails.startTime = startTimeRaw;
    }

    let startTimeFormatted = null;
    if (startTimeRaw) {
      const parsedDate = new Date(startTimeRaw);
      if (!Number.isNaN(parsedDate.getTime())) {
        try {
          const formatter = new Intl.DateTimeFormat(undefined, {
            dateStyle: 'full',
            timeStyle: 'short',
            timeZone: timeZone || undefined
          });
          startTimeFormatted = formatter.format(parsedDate);
        } catch (err) {
          startTimeFormatted = parsedDate.toLocaleString();
        }
      } else {
        startTimeFormatted = startTimeRaw;
      }
    }

    window.dataLayer.push({
      event: 'book_appointment_conversion',
      value: 1,
      currency: 'USD',
      bookingDetails: bookingDetails
    });

    if (name) {
      const heading = document.querySelector('h1');
      if (heading) {
        heading.textContent = `Thanks for booking your SRA, ${name}!`;
      }
    }

    const detailTarget = document.getElementById('booking-details');
    if (detailTarget) {
      const fragments = [];

      if (email) {
        fragments.push(`We sent the confirmation to ${email}.`);
      }

      if (startTimeFormatted) {
        const timeMessage = timeZone ? `${startTimeFormatted} (${timeZone})` : startTimeFormatted;
        fragments.push(`We'll meet on ${timeMessage}.`);
      }

      if (eventType) {
        fragments.push(`You're booked for the ${eventType.replace(/[-_]/g, ' ')} session.`);
      }

      if (location) {
        fragments.push(`Location: ${location}.`);
      }

      if (fragments.length > 0) {
        const infoParagraph = document.createElement('p');
        infoParagraph.textContent = fragments.join(' ');
        detailTarget.appendChild(infoParagraph);
      }

      const isLikelyLink = (value) => /^[a-zA-Z][a-zA-Z0-9+.\-]*:/.test(value) || value.startsWith('/');

      if ((meetingUrl && isLikelyLink(meetingUrl)) || rescheduleLink || cancelLink) {
        const linksParagraph = document.createElement('p');

        if (meetingUrl && isLikelyLink(meetingUrl)) {
          const meetingAnchor = document.createElement('a');
          meetingAnchor.href = meetingUrl;
          meetingAnchor.textContent = 'Join the meeting';
          meetingAnchor.rel = 'noopener';
          linksParagraph.appendChild(meetingAnchor);
        }

        const addLink = (href, label) => {
          if (!href) return;
          if (linksParagraph.childNodes.length > 0) {
            linksParagraph.appendChild(document.createTextNode(' · '));
          }
          const anchor = document.createElement('a');
          anchor.href = href;
          anchor.textContent = label;
          anchor.rel = 'noopener';
          linksParagraph.appendChild(anchor);
        };

        addLink(rescheduleLink, 'Reschedule');
        addLink(cancelLink, 'Cancel');

        if (linksParagraph.childNodes.length > 0) {
          detailTarget.appendChild(linksParagraph);
        }
      }
    }
  })();
</script>
