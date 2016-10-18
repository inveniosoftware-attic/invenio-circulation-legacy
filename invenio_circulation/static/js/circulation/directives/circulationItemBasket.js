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
    .module('circulationItemBasket')
    .directive('circulationItemBasket', circulationItemBasket);

  circulationItemBasket.$inject = [
    '$http',
    'circulationItemStore',
    'circulationUserStore',
    'circulationSettingsStore',
  ];

  function circulationItemBasket(
      $http, 
      circulationItemStore,
      circulationUserStore,
      circulationSettingsStore
  ) {
    var directive = {
      link: link,
      scope: true,
      templateUrl: templateUrl,
    };

    return directive;

    function link(scope, element, attributes) {
      scope.items = circulationItemStore.items;
      scope.remove = function(index) {
        circulationItemStore.items.splice(index, 1);
      }
      scope.loan = function() {
        var data = {
          'user_id': circulationUserStore.user.id,
        };
        performAction(attributes.loanEndpoint, data);
      }
      scope.request = function() {
        var data = {
          'user_id': circulationUserStore.user.id,
        };
        performAction(attributes.requestEndpoint, data);
      }
      scope.return = function() {
        var data = {};
        performAction(attributes.returnEndpoint, data);
      }
    }

    function performAction(actionEndpoint, data) {
      angular.forEach(circulationItemStore.items, function(item, index) {
        var send_data = angular.copy(data);
        send_data.item_id = item.id;
        angular.extend(send_data, circulationSettingsStore.getPayload());

        $http({
          method: 'POST',
          url: actionEndpoint,
          headers: {
            'Content-Type': 'application/json'
          },
          data: send_data,
        });
      })
    }

    function templateUrl(element, attrs) {
      return attrs.template;
    }
  }
})(angular);
