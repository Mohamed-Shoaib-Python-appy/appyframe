context.skip("Permissions API", () => {
	before(() => {
		cy.visit("/login");
		cy.remove_role("appyframe@example.com", "System Manager");
		cy.visit("/app");
	});

	it("Checks permissions via `has_perm` for Kanban Board DocType", () => {
		cy.visit("/app/kanban-board/view/list");
		cy.window()
			.its("appyframe")
			.then((appyframe) => {
				appyframe.model.with_doctype("Kanban Board", function () {
					// needed to make sure doc meta is loaded
					expect(appyframe.perm.has_perm("Kanban Board", 0, "read")).to.equal(true);
					expect(appyframe.perm.has_perm("Kanban Board", 0, "write")).to.equal(true);
					expect(appyframe.perm.has_perm("Kanban Board", 0, "print")).to.equal(false);
				});
			});
	});

	it("Checks permissions via `get_perm` for Kanban Board DocType", () => {
		cy.visit("/app/kanban-board/view/list");
		cy.window()
			.its("appyframe")
			.then((appyframe) => {
				appyframe.model.with_doctype("Kanban Board", function () {
					// needed to make sure doc meta is loaded
					const perms = appyframe.perm.get_perm("Kanban Board");
					expect(perms.read).to.equal(true);
					expect(perms.write).to.equal(true);
					expect(perms.rights_without_if_owner).to.include("read");
				});
			});
	});

	after(() => {
		cy.add_role("appyframe@example.com", "System Manager");
		cy.call("logout");
	});
});
