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
    .directive('circulationUserHoldings', circulationUserHoldings);

  circulationUserHoldings.$inject = ['$http', 'circulationUserHoldingsStore'];

  function circulationUserHoldings($http, circulationUserHoldingsStore) {
    var directive = {
      link: link,
      scope: true,
      templateUrl: templateUrl,
    };

    return directive;

    function link(scope, element, attributes) {
      scope.requestedEndDate = '',

      $http({
        method: 'GET',
        url: attributes.searchEndpoint,
        headers: {
          'Content-Type': 'application/json'
        },
        params: {q: attributes.query + attributes.currentUserId},
      }).then(function(response) {
        circulationUserHoldingsStore.setHoldings(response.data.hits.hits,
                                                 attributes.currentUserId);
        scope.loans = circulationUserHoldingsStore.loans;
        scope.requests = circulationUserHoldingsStore.requests;
      });

      scope.extend = function(itemId) {
        var data = {
          item_id: itemId,
        };

        if (scope.requestedEndDate != '') {
          data.requested_end_date = scope.requestedEndDate;
        }

        $http({
          method: 'POST',
          url: attributes.extendEndpoint,
          headers: {
            'Content-Type': 'application/json'
          },
          data: data,
        });

      };

      scope.lose = function(itemId) {
        $http({
          method: 'POST',
          url: attributes.loseEndpoint,
          headers: {
            'Content-Type': 'application/json'
          },
          data: {
            item_id: itemId,
          },
        }).then(function(response) {
        });
      };

      scope.cancel = function(itemId, holdId) {
        $http({
          method: 'POST',
          url: attributes.cancelEndpoint,
          headers: {
            'Content-Type': 'application/json'
          },
          data: {
            item_id: itemId,
            hold_id: holdId,
          },
        }).then(function(response) {
        });
      };
    }

    function templateUrl(element, attrs) {
      return attrs.template;
    }
  }
})(angular);
