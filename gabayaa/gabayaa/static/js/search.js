$(document).ready(function () {
  function performSearch(query) {
    var searchUrl = $("#search-results").data("search-url"); // Retrieve the URL from the data attribute
    $.ajax({
      type: "GET",
      url: searchUrl,
      data: { q: query },
      success: function (data) {
        var results = $("#search-results");
        var searchQueryMessage = $("#search-query-message"); // Select the span element

        console.log("data: " + data);
        results.empty();
        if (query) {
          searchQueryMessage.text("search result for: " + "'" + query + "'");
        } else {
          searchQueryMessage.text(""); // Clear the content if no query
        }
        $.each(data.customers, function (index, customer) {
          var listItem = $("<li class='list-group-item'></li>");
          var updateCustomerUrl = $("#search-results").data(
            "update-customer-url"
          );

          var url = updateCustomerUrl.replace("-1", customer.id);
          var link = $('<a href="' + url + '">' + customer.username + "</a>");
          console.log("link: " + link);
          listItem.append(link);
          listItem.append(
            "<p class='list-group-item'>is super user - " +
              customer.is_superuser +
              "</p>"
          );
          results.append(listItem);
        });
      },
    });
  }

  // Listen to changes in the search input
  $("#search-input").on("input", function () {
    var query = $(this).val();
    performSearch(query);
  });

  // Prevent the default form submission on Enter key press
  // $("#search-input").on("keypress", function (e) {
  //   if (e.which === 13) {
  //     e.preventDefault();
  //   }
  // });
});
