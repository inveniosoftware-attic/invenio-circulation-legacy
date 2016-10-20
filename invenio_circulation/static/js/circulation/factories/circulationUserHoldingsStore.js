/*
 * This file is part of invenio.
 * Copyright (C) 2016 CERN.
 *
 * invenio is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License as
 * published by the Free Software Foundation; either version 2 of the
 * License, or (at your option) any later version.
 *
 * invenio is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with invenio; if not, write to the Free Software Foundation, Inc.,
 * 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
 *
 * In applying this license, CERN does not
 * waive the privileges and immunities granted to it by virtue of its status
 * as an Intergovernmental Organization or submit itself to any jurisdiction.
 */


(function (angular) {
  // Setup
  angular
    .module('circulationUserHub')
    .factory('circulationUserHoldingsStore', circulationUserHoldingsStore);

  function circulationUserHoldingsStore() {
    var loans = [];
    var requests = [];

    var service = {
      loans: loans,
      requests: requests,
      setHoldings: setHoldings,
    };

    return service;

    function setHoldings(items, currentUserId) {
      var today = new Date();
      angular.forEach(items, function(item) {
        var status = item.metadata._circulation.status;
        angular.forEach(item.metadata._circulation.holdings, function(holding) {
          if (holding.user_id == currentUserId) {
            holding.itemId = item.id;
            if (Date.parse(holding.start_date) <= today &&
                status == 'on_loan') {
              loans.push(holding);
            } else {
              requests.push(holding);
            }
          }
        });
      });
    }
  }
})(angular);
