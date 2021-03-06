/*
 * WARNING: You must use the same name as the module !
 */
openerp.inouk_tree_widgets8 = function(instance, local) {
    var _t = instance.web._t,
        _lt = instance.web._lt;

    var QWeb = instance.web.qweb;

    // TODO: extend openerp.web.search.Field when ready
    local.HomePage = instance.Widget.extend({
        className: 'ik_home',
        start: function() {
            var msg = "InoukTree => HomePage started !!!";
            console.log(msg)
            this.$el.append("<div>"+msg+"</div>");

            var greeting = new local.GreetingWidget(this);  // Here this defines the widget's parent
            // TODO: Why do we need to return ?
            greeting.appendTo(this.$el);

            var ikTree = new local.IKSearchTreeSelectionField(this);  // Here this defines the widget's parent
            ikTree.appendTo(this.$el);
        }
    });

    local.GreetingWidget = instance.Widget.extend({
        className: 'ik_greeting',
        start: function() {
            this.$el.append("<div>Hello! I'm greeting widget </div>");
        }
    });

    local.IKSearchTreeSelectionField = instance.Widget.extend({
        // className is useless with template as the template root becomes the widget
        // root element
        // className: 'ik_tree',

        template: 'IKSearchTreeSelectionField',

        init: function(parent) {
            this._super(parent); // DO NOT FORGET THIS
            this.variable = "Cyril"; // This will be reachable by template
        },

        start: function() {
            console.log("IKSearchTreeSelectionField started()");
        },

        events: {
            'click': 'widget_clicked'
        },

        widget_clicked: function(evt) {
            var self = this;
            openerp.session.rpc('/inouk-tree/ping', { ka1: 3, ka2: 'coucou' }).then(
                function(result) {
                    self.$el.append("<div>result="+result+"</div>");
                    console.log("result="+result);
                },
                function(error) {
                    console.log(error);
                }
            );
        }
    });

    /*
     * My First component
     *
     * TODO: Document component parameters/attributes
     *
     */
    // TODO: CSS use same font as char

    local.InoukTree2One = instance.web.form.AbstractField.extend(instance.web.form.ReinitializeFieldMixin, {
        template: "InoukTree2One",

        TREE_ELEMENT_TEMPLATE:          '<div class="ikt2o-container" style="position:relative;z-index:9;"></div>',
        TREE_TOGGLE_SHORTCUT_KEYCODE:   115,      // F4

        TREE_DEFAULT_HEIGHT:            200,      // pixels
        TREE_DEFAULT_FILTER_LEAVES_ONLY:false,    // search on all nodes
        TREE_DEFAULT_FILTER_MODE:       'dimm',   // 'dimm' | 'hide'
        TREE_DEFAULT_TITLE_COMPONENTS_SEPARATOR: " ➥ ", // Used to split name and extract node name

        events: {
            'keyup input': function (evt) {
                console.debug("ikt:keyup input event")
                self = this;
                if (self.$inouk_tree.is(":visible")) {
                    var filterString = self.$input.val(),
                        tree = self.$inouk_tree.fancytree('getTree');
                    n = tree.filterNodes(filterString, self.TREE_DEFAULT_FILTER_LEAVES_ONLY);
                }
            }
        },

        init: function(field_manager, node) {
            console.debug("ik:init()");
            this._super.apply(this, arguments);

            // this.value : contains the effective value of the field: an id
            this.display_value = "";  // label associated to this.value id
            this.current_display = null;
            this.is_started = false;

            /*
             * process tag parameter
             */
            this.search_mode = node.attrs.tree_search_mode === 'server' ? 'server' : 'client';
            this.parent_field_name = node.attrs.tree_parent_field_name;
            this.order_by = node.attrs.tree_order_by;
            this.children_field_name = node.attrs.tree_children_field_name;
            this.title_field_name = node.attrs.tree_title_field_name;
            this.tree_height = node.attrs.tree_height || this.TREE_DEFAULT_HEIGHT;  // in pixels
            this.filter_mode = node.attrs.tree_filter_mode || '' in ['dimm', 'hide'] ? node.attrs.tree_filter_mode : 'hide';
            this.expand_nodes = node.attrs.tree_expand_nodes || false;
            this.tree_title_components_separator = node.attrs.tree_title_components_separator || this.TREE_DEFAULT_TITLE_COMPONENTS_SEPARATOR;

        },

        /*
         * Only (ugly) solution to hide tree when it loose focus.
         *  When user click outside tree and if tree is visible we hide it
         */
        initialize_field: function() {
            this.is_started = true;

            instance.web.bus.on('click', this, function (evt) {
                if (!this.get("effective_readonly") && this.$input && this.$inouk_tree.is(':visible')) {
                    this.$inouk_tree.hide();
                }
            });

            instance.web.form.ReinitializeFieldMixin.initialize_field.call(this);
        },

        /*
         * render_value()
         *  called each time value is modified to redisplay it.
         *  Overriden to handle value / display_value duality
         */
        render_value: function() {
            var self = this;

            console.debug("ikt:render_value()");
            console.debug("  ikt:render_value() this.get('value') = "+this.get('value'));
            console.debug("  ikt:render_value() this.display_value = "+this.display_value);

            if (!this.get("value")) {
                this.display_string("");
                return;
            }
            if (this.display_value) {
                this.display_string(this.display_value);
                //return;
            }
        },

        /*
         * display_string(str)
         *  Generate displayed string in readonly mode with a link to open referenced
         *  object.
         */
        display_string: function(str) {
            console.debug("ikt::display_string()");
            var self = this;
            if (!this.get("effective_readonly")) {

                // TODO: understand why display string is called before render editable (compared to many2one) and (re)move this
                this.$input = this.$el.find("input");

                var nodeTitle = (str.split("\n")[0]).split(self.tree_title_components_separator);
                nodeTitle = nodeTitle[nodeTitle.length - 1];

                this.$input.val(nodeTitle);
                this.current_display = this.$input.val();
                if (this.is_false()) {
                    this.$('.oe_m2o_cm_button').css({'display':'none'});
                } else {
                    this.$('.oe_m2o_cm_button').css({'display':'inline'});
                }

            } else {
                var lines = _.escape(str).split("\n");
                var link = "";
                var follow = "";
                link = lines[0];
                follow = _.rest(lines).join("<br />");
                if (follow)
                    link += "<br />";
                    link += "<br />";
                var $link = this.$el.find('.oe_form_uri')
                    .unbind('click')
                    .html(link);
                if (! this.options.no_open)
                    $link.click(function () {
                        var context = self.build_context().eval();
                        var model_obj = new instance.web.Model(self.field.relation);
                        model_obj.call('get_formview_action', [self.get("value"), context]).then(function(action){
                            self.do_action(action);
                        });
                        return false;
                    });
                $(".oe_form_m2o_follow", this.$el).html(follow);
            }
        },


        /*
         * render_editable()
         *  called each time view mode switch from readonly to editable by ini
          *  (read, edit). It is NOTcalled when user navigates
         *  objects using the top right arrows (in this case, only render_value() is called.)
         *
         *  So behaviour is different based on this.effective_readonly value:
         *   true: we create the tree
         *   false: we destroy it if it exists
         */
        render_editable: function() {
            var self = this;
            console.debug("ikt:render_editable()");
            console.debug("  ikt:effective_readonly => " + this.get('effective_readonly'));

            /*
             * we must move the fancytree div outside odoo views to be able to
             * play with z-index. Selector below comes from Many2one.render_editable()
             */
            var appendTo = this.$el.parents('.oe_view_manager_body, .modal-dialog').last();
            if (appendTo.length === 0){
                appendTo = '.oe_application > *';
            }
            this.appendTo = appendTo;

            this.$input = this.$el.find("input");
            this.$inouk_tree = $(this.TREE_ELEMENT_TEMPLATE).appendTo(appendTo);

            this.$inouk_tree.fancytree({
                extensions: ["filter"],
                quicksearch: true,
                autoActivate: false,    // We do not want nodes to be activated by a keystroke
                //focusOnSelect: true,    //
                filter: {
                    mode: self.filter_mode,
                    autoApply: true
                },
                activate: function (event, data) {
                    console.debug("ikt::fancytree::activate() => set_value(", data.node.key, ", ",data.node.title, ");");
                    var value = [data.node.key, data.node.title];
                    self.set_value(value);
                    self.$inouk_tree.hide();
                    event.stopPropagation();
                    self.$input.focus();
                },

                /*
                 * click
                 * We prevent click propagation since we use this event outside
                 * the tree to close it.
                 *    see initialize_field() above
                 */
                click: function(evt, data) {
                    evt.stopPropagation();
                    return true
                },

                /*
                 * On F4 and ESCAPE we close the tree and get back to the input field
                 */
                keydown: function(evt, data) {
                    if(evt.which==self.TREE_TOGGLE_SHORTCUT_KEYCODE || evt.which== $.ui.keyCode.ESCAPE) {
                        self.$inouk_tree.hide();
                        self.$input.focus();
                        return false;   // We don't want the key to be processed by input in case
                                        // TREE_TOGGLE_SHORTCUT_KEYCODE code is a normal key with modifier.
                    } else if(evt.which==$.ui.keyCode.TAB) {
                        // Prevent tab from exiting the treeview
                        return false;
                    }
                    return true; // Let fancytree process the event
                },

                /*
                 * Data initialization
                 */
                source: openerp.session.rpc(
                    '/inouk-tree/tree',
                    {
                        search_mode: self.search_mode,
                        model_name: self.field.relation,
                        title_field_name: self.title_field_name,
                        parent_field_name: self.parent_field_name,
                        children_field_name: self.children_field_name,
                        domain: self.build_domain().eval() || [],
                        expand_nodes: self.expand_nodes,
                        order_by: self.order_by,
                        parent_id: null
                    }
                ),
                /*
                 * Subsequent node lazy loading
                 */
                lazyLoad: function (event, data) {
                    data.result = openerp.session.rpc(
                        '/inouk-tree/nodes',
                        {
                            search_mode: self.search_mode,
                            model_name: self.field.relation,
                            title_field_name: self.title_field_name,
                            parent_field_name: self.parent_field_name,
                            children_field_name: self.children_field_name,
                            domain: self.build_domain().eval() || [],
                            expand_nodes: self.expand_nodes,
                            order_by: self.order_by,
                            parent_id: data.node.key
                        }
                    )
                }
            })
                .detach()
                .appendTo(appendTo)
                .width(this.$el.width())
                .position({ my: "left top", at: "left bottom", of: this.$el})
                .hide();
                //.css('visibility', 'visible');

            // height must be defined directly on the fancy tree ul element
            this.$fancytree = this.$inouk_tree.find('ul.fancytree-container');
            this.$fancytree.height(this.tree_height);

            /*
             * Setup dropdown button behaviour
             */
            // TODO: Rework method name and refactor to reuse component
            var open_tree_event_handler = function(evt) {
                // TODO: Should'nt this be invoked in caller ???
                evt.stopPropagation();  // We must prevent bubbling on main

                if (self.$inouk_tree.is(":visible")) {
                    self.$inouk_tree.hide();
                    self.$input.focus();
                    return
                } else {
                    /*
                     * We must reload tree content.
                     * We use fancytree reload() method which is is supposed to use
                     * default source but it does not.
                     * So we pass it the same source promise as the one we use to
                     * initialize the tree.
                     * TODO: remove duplicated source definition when fixed in fancytree
                     * TODO: implement current value value selection in tree
                     if (self.get("value") && ! self.floating) {
                     self.$input.autocomplete("search", "");
                     } else {
                     self.$input.autocomplete("search");
                     }
                     */
                    console.debug("  ikt:reload_tree()");
                    self.$inouk_tree.fancytree('getTree').reload(
                        openerp.session.rpc('/inouk-tree/tree',
                            {
                                search_mode: self.search_mode,
                                model_name: self.field.relation,
                                title_field_name: self.title_field_name,
                                parent_field_name: self.parent_field_name,
                                children_field_name: self.children_field_name,
                                domain: self.build_domain().eval() || [],
                                expand_nodes: self.expand_nodes,
                                order_by: self.order_by,
                                parent_id: null
                            })
                    );

                    /*
                     * We update tree position to accomodate window resizing
                     * TODO: Which option below is better ?
                     */
                    /* Option 1
                     self.$inouk_tree.css('visibility', 'hidden');
                     self.$inouk_tree.show();  // We must show it before repositioning
                     self.$inouk_tree.position({ my: "left top", at: "left bottom", of: self.$el});
                     self.$inouk_tree.css('visibility', 'visible');
                     */
                    /* Option 2 : flickering ? */
                    self.$inouk_tree.show();  // We must show it before repositioning
                    self.$inouk_tree.position({ my: "left top", at: "left bottom", of: self.$el});
                }
            };

            this.$drop_down = this.$el.find(".oe_m2o_drop_down_button");
            this.$drop_down.click(open_tree_event_handler);


            var input_change_handler = function(evt) {
                console.log("ikt::input_change_handler()");
                console.log("ikt::input_change_handler  self.$input.val() = ", self.$input.val());
                console.log("ikt::input_change_handler  self.current_display = ", self.current_display);
                console.log("ikt::input_change_handler  keyup evt.which = ", evt.which);

                // Did user modify input field content ?
                if (self.current_display !== self.$input.val()) {
                    self.current_display = self.$input.val();

                    // Did user reset input content ?
                    if (self.$input.val() === "") {
                        self.internal_set_value(false);
                        self.floating = false;
                    } else {
                        self.floating = true;
                    };

                    // TODO: Create a derived ui tree component to remove following duplicated code

                    // Content has been modified ; we show the tree
                    if (!self.$inouk_tree.is(":visible")) {
                        console.debug("  ikt:reload_tree()");
                        self.$inouk_tree.fancytree('getTree').reload(
                            openerp.session.rpc('/inouk-tree/tree',
                                {
                                    search_mode: self.search_mode,
                                    model_name: self.field.relation,
                                    title_field_name: self.title_field_name,
                                    parent_field_name: self.parent_field_name,
                                    children_field_name: self.children_field_name,
                                    domain: self.build_domain().eval() || [],
                                    expand_nodes: self.expand_nodes,
                                    order_by: self.order_by,
                                    parent_id: null
                                })
                        );
                        self.$inouk_tree.show();  // We must show it before repositioning
                        self.$inouk_tree.position({ my: "left top", at: "left bottom", of: self.$el});
                    }
                }
            };

            this.$input.change(input_change_handler);
            this.$input.keyup(input_change_handler);

            /**
             * event: keydown
             *
             */
            this.$input.keydown(function(evt){
                console.debug("keydown evt.which=",evt.which," evt.ctrlKey=",evt.ctrlKey);
                if(evt.which==self.TREE_TOGGLE_SHORTCUT_KEYCODE) {
                    /*
                     * User press TREE_TOGGLE_SHORTCUT_KEYCODE
                     *   if tree is  visible : we focus on it
                     *           not visible : we show it but don't focus it
                     */
                    if(self.$inouk_tree.is(":visible")) {
                        evt.stopPropagation();  // We don't want TREE_TOGGLE_SHORTCUT_KEYCODE to be processed by input
                        self.$fancytree.focus();
                    } else {
                        open_tree_event_handler(evt)
                    }
                } else if(evt.which== $.ui.keyCode.TAB) {
                    /*
                     * User press TAB, we hide the tree and let std behavior happens
                     */
                    if (self.$inouk_tree.is(":visible"))
                        self.$inouk_tree.hide();
                }
            })
        },

        /*
         * Called by the view to set field's value.
         * Overloaded to handle m2o specific value format: [4, "Object name"]
         */
        set_value: function(value_) {
            console.debug("ikt::set_value("+value_+")");
            var self = this;
            if (value_ instanceof Array) {
                this.display_value = value_[1];
                value_ = value_[0];
            }
            value_ = value_ || false;
            this.reinit_value(value_);
        },

        reinit_value: function(val) {
            console.debug("ikt::reinit_value("+ val +")");
            this.internal_set_value(val);
            this.floating = false;
            // TODO: implemente if (this.is_started && !this.no_rerender)
                this.render_value();
        },

        /*
         * set_dimensions()
         *   Handle INPUT height modification (this code comes from Many2OneWidget)
         *   Note that Tree view height is defined using the tree_height field's attribute.
         */
        set_dimensions: function (height, width) {
            this._super(height, width);
            if (!this.get("effective_readonly") && this.$input)
                this.$input.css('height', height);
        },

        /*
         * destroy()
         *   called when the view is destroyed to destroy what has been created by
         *   this widget.
         *   In our case we rely on destroy_content from ReinitializeFieldMixin below
         */
        destroy: function () {
            console.debug("ikt::destroy()");
            this.destroy_content();  // from ReinitializeFieldMixin
            return this._super();
        },

        /*****
         *
         *      ReinitializeFieldMixin
         *        For fields that must completely rerender when readonly state is changed.
         *        Each time effective_readonly is modified, call:
         *          destroy_content()
         *          renderElement()
         *          initialize_content()
         */

        /*
         * initialize_content()
         *   Called by Client to initialize content
         */
        initialize_content: function() {
            console.debug("ikt::initialize_content()");
            console.debug("  ikt::  self.effective_readonly="+this.get('effective_readonly'));
            // TODO: What about in readonly mode ?
            if (!this.get("effective_readonly"))
                this.render_editable();
        },

        /*
         * destroy_content()
         *   Must destroy what have been
         */
        destroy_content: function() {
            console.debug("ikt::destroy_content()");
            // TODO: destroy what has been created by this widget from initialize content
            if(this.$inouk_tree) {
                this.$inouk_tree.remove();
                delete this.$inouk_tree;

            }
        }


    });

    instance.web.form.widgets.add('inouktree2one',                  'instance.inouk_tree_widgets8.InoukTree2One');
    instance.web.client_actions.add('inouk_tree_widgets8.homepage', 'instance.inouk_tree_widgets8.HomePage');
};
