/* ============================================================
   REFLEXION JOURNAL — JS Propio
   Reemplaza Bootstrap JS y npm.js
   Sin dependencias externas (jQuery se mantiene solo para AJAX)
   ============================================================ */

(function () {
    'use strict';

    /* ==================== MODALES ==================== */

    function openModal(id) {
        var el = document.getElementById(id);
        if (!el) return;
        el.classList.add('is-open');
        document.body.style.overflow = 'hidden';
        el.dispatchEvent(new CustomEvent('modal:open', { bubbles: true }));
    }

    function closeModal(id) {
        var el = document.getElementById(id);
        if (!el) return;
        el.classList.remove('is-open');
        document.body.style.overflow = '';
        el.dispatchEvent(new CustomEvent('modal:close', { bubbles: true }));
    }

    /* Cerrar modal al hacer click en el overlay (fuera del box) */
    document.addEventListener('click', function (e) {
        if (e.target.classList && e.target.classList.contains('modal-overlay')) {
            e.target.classList.remove('is-open');
            document.body.style.overflow = '';
        }
    });

    /* data-modal-open="#id" → abre modal */
    document.addEventListener('click', function (e) {
        var btn = e.target.closest('[data-modal-open]');
        if (btn) {
            var target = btn.getAttribute('data-modal-open').replace('#', '');
            openModal(target);
        }
    });

    /* data-modal-close → cierra el modal contenedor */
    document.addEventListener('click', function (e) {
        var btn = e.target.closest('[data-modal-close]');
        if (btn) {
            var overlay = btn.closest('.modal-overlay');
            if (overlay) closeModal(overlay.id);
        }
    });

    /* Compatibilidad jQuery: $.fn.modal('show'/'hide') */
    if (typeof jQuery !== 'undefined') {
        jQuery.fn.modal = function (action) {
            var self = this;
            if (action === 'show') {
                self.each(function () { openModal(this.id); });
            } else if (action === 'hide') {
                self.each(function () { closeModal(this.id); });
            }
            /* Simular .on('shown.bs.modal', ...) disparando evento nativo */
            var origOn = self.on.bind(self);
            self.on = function (event, handler) {
                if (event === 'shown.bs.modal') {
                    self.each(function () {
                        this.addEventListener('modal:open', handler);
                    });
                    return self;
                }
                return origOn(event, handler);
            };
            return self;
        };
    }

    /* ==================== ALERTAS ==================== */

    document.addEventListener('click', function (e) {
        var btn = e.target.closest('.close[data-dismiss="alert"]') ||
                  e.target.closest('.alert-close');
        if (btn) {
            var alert = btn.closest('.alert');
            if (alert) alert.style.display = 'none';
        }
    });

    /* ==================== DROPDOWN ==================== */

    document.addEventListener('click', function (e) {
        var toggle = e.target.closest('.dropdown-toggle');
        if (toggle) {
            e.preventDefault();
            var dropdown = toggle.closest('.dropdown');
            if (!dropdown) return;

            var isOpen = dropdown.classList.contains('is-open');

            /* Cerrar todos los dropdowns abiertos */
            document.querySelectorAll('.dropdown.is-open').forEach(function (d) {
                d.classList.remove('is-open');
            });

            if (!isOpen) dropdown.classList.add('is-open');
            return;
        }

        /* Clic fuera → cerrar dropdowns */
        if (!e.target.closest('.dropdown')) {
            document.querySelectorAll('.dropdown.is-open').forEach(function (d) {
                d.classList.remove('is-open');
            });
        }
    });

    /* ==================== NAVBAR MOBILE ==================== */

    document.addEventListener('click', function (e) {
        var toggle = e.target.closest('.navbar-toggle');
        if (!toggle) return;
        var targetSel = toggle.getAttribute('data-target');
        var menu = document.querySelector(targetSel);
        if (menu) menu.classList.toggle('is-open');
    });

    /* ==================== ACORDEÓN / FAQ ==================== */

    document.addEventListener('click', function (e) {
        /* Acordeón propio (.rj-accordion-btn) */
        var accBtn = e.target.closest('.rj-accordion-btn');
        if (accBtn) {
            var item = accBtn.closest('.rj-accordion-item');
            if (item) item.classList.toggle('is-open');
            return;
        }

        /* Acordeón Bootstrap legacy (.panel-group a[data-toggle="collapse"]) */
        var legacyBtn = e.target.closest('[data-toggle="collapse"]');
        if (legacyBtn) {
            e.preventDefault();
            var targetSel = legacyBtn.getAttribute('href') ||
                            legacyBtn.getAttribute('data-target');
            if (!targetSel) return;
            var content = document.querySelector(targetSel);
            if (!content) return;
            var isOpen = content.classList.contains('in');
            /* Cerrar todos en el mismo group */
            var parent = legacyBtn.getAttribute('data-parent');
            if (parent) {
                document.querySelectorAll(parent + ' .panel-collapse.in')
                    .forEach(function (c) { c.classList.remove('in'); });
            }
            if (!isOpen) content.classList.add('in');
        }
    });

    /* ==================== TOGGLE CONTRASEÑA ==================== */

    document.addEventListener('click', function (e) {
        var btn = e.target.closest('.toggle-password');
        if (!btn) return;
        var targetId = btn.getAttribute('data-target');
        var input = document.getElementById(targetId);
        if (!input) return;
        var icon = btn.querySelector('i');
        if (input.type === 'password') {
            input.type = 'text';
            if (icon) {
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            }
        } else {
            input.type = 'password';
            if (icon) {
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        }
    });

    /* ==================== API PÚBLICA ==================== */
    window.RJ = { openModal: openModal, closeModal: closeModal };

})();
