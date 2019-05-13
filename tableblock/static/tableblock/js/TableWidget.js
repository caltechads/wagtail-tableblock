'use strict';

function initTable(id, tableOptions) {
    var containerId = id + '-handsontable-container';
    var tableHeaderCheckboxId = id + '-handsontable-header';
    var colHeaderCheckboxId = id + '-handsontable-col-header';
    var hiddenStreamInput = $('#' + id);
    var tableHeaderCheckbox = $('#' + tableHeaderCheckboxId);
    var colHeaderCheckbox = $('#' + colHeaderCheckboxId);
    var hot;
    var defaultOptions;
    var finalOptions = {};
    var persist;
    var cellEvent;
    var structureEvent;
    var dataForForm = null;
    function getHeight() {
        var tableParent = $('#' + id).parent();
        return tableParent.find('.htCore').height() + (tableParent.find('.input').height() * 2);
    }

    // To ensure that the table is rendered at the appropriate size, we need to apply some width and height settings
    // to various elements within the widget, to override handsontable's defaults.
    var resizeTargets = ['.input > .handsontable', '.wtHider', '.wtHolder'];
    function resizeHeight() {
        // TODO: There's a small bug in here, but I'm not sure how best to address it. When removing a row, the
        //  .wtHolder and the .handsontable get their heights set a little too tall. The .wtHider somehow gets its
        //  height set to the correct value at some point later, but the other two stay with the wrong value.
        var currTable = $('#' + id);
        $.each(resizeTargets, function() {
            currTable.closest('.field-content').find(this).height(getHeight());
        });
    }
    function resizeWidth(width) {
        $.each(resizeTargets, function() {
            $(this).width(width);
        });
    }

    try {
        dataForForm = JSON.parse(hiddenStreamInput.val());
    } catch (e) {
        // do nothing
    }

    if (dataForForm !== null) {
        if (dataForForm.hasOwnProperty('first_row_is_table_header')) {
            tableHeaderCheckbox.prop('checked', dataForForm.first_row_is_table_header);
        }
        if (dataForForm.hasOwnProperty('first_col_is_header')) {
            colHeaderCheckbox.prop('checked', dataForForm.first_col_is_header);
        }
    }

    if (!tableOptions.hasOwnProperty('width')) {
        // Size to parent .field-content width if width is not given in tableOptions.
        $(window).on('resize', function() {
            hot.updateSettings({
                width: '100%',
            });
            resizeWidth('100%');
        });
    }

    if (!tableOptions.hasOwnProperty('height')) {
        // Size to appropriate height if height is not given in tableOptions.
        $(window).on('resize', function() {
            hot.updateSettings({
                height: getHeight()
            });
        });
    }

    persist = function() {
        hiddenStreamInput.val(JSON.stringify({
            data: hot.getData(),
            first_row_is_table_header: tableHeaderCheckbox.prop('checked'),
            first_col_is_header: colHeaderCheckbox.prop('checked')
        }));
    };

    cellEvent = function(change, source) {
        if (source === 'loadData') {
            // Don't save this change.
            return;
        }
        persist();
        // This is needed because the user might insert muleiple lines of data in a single table row, which may require
        // the table to get taller.
        resizeHeight();
    };

    // noinspection JSUnusedLocalSymbols
    structureEvent = function(index, amount) {
        resizeHeight();
        persist();
    };

    tableHeaderCheckbox.on('change', function() {
        persist();
    });

    colHeaderCheckbox.on('change', function() {
        persist();
    });

    defaultOptions = {
        afterChange: cellEvent,
        afterCreateCol: structureEvent,
        afterCreateRow: structureEvent,
        afterRemoveCol: structureEvent,
        afterRemoveRow: structureEvent,
        // contextMenu set via init, from server defaults
    };

    if (dataForForm !== null && dataForForm.hasOwnProperty('data')) {
        // Overrides default value from tableOptions (if given) with value from database
        defaultOptions.data = dataForForm.data;
    }

    Object.keys(defaultOptions).forEach(function (key) {
        finalOptions[key] = defaultOptions[key];
    });
    Object.keys(tableOptions).forEach(function (key) {
        finalOptions[key] = tableOptions[key];
    });

    hot = new Handsontable(document.getElementById(containerId), finalOptions);
    // Call to render() removes 'null' literals from empty cells
    hot.render();

    // Apply resize after document is finished loading (parent .field-content width is set).
    if ('resize' in $(window)) {
        resizeHeight();
        $(window).on('load', function() {
            $(window).trigger('resize');
        });
    }
}
