from decimal import Decimal
from datetime import timedelta

from django.contrib.admin.models import ADDITION, LogEntry
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import (
    AdminProfile,
    CollectionRecord,
    Customer,
    CustomerKYCDocument,
    EBankingCredential,
    RecycleBinItem,
    Ticket,
    Transaction,
    WebsitePopup,
)


class AdminInterfaceTests(TestCase):
    def setUp(self):
        self.superuser = get_user_model().objects.create_superuser(
            username="dashboard-admin",
            email="admin@example.com",
            password="test-password",
        )
        self.client.force_login(self.superuser)

    def test_admin_index_contains_the_custom_real_admin_dashboard(self):
        response = self.client.get(reverse("admin:index"))
        staff_profile_url = reverse("admin:myapp_staff_profile_settings")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="admin-dashboard"')
        self.assertContains(response, "Today's Collection")
        self.assertContains(response, "Recent Daily Collection Work")
        self.assertContains(response, "Staff Collection Performance")
        self.assertContains(response, "KYC Status")
        self.assertContains(response, 'class="admin-menu-grid"')
        self.assertContains(response, 'class="admin-menu-card"')
        self.assertContains(response, reverse("admin:auth_user_changelist"))
        self.assertContains(response, reverse("admin:auth_group_changelist"))
        self.assertContains(response, reverse("admin:myapp_banner_changelist"))
        self.assertContains(response, reverse("admin:myapp_notice_changelist"))
        self.assertContains(response, reverse("admin:myapp_reports"))
        self.assertContains(response, reverse("admin:myapp_recyclebinitem_changelist"))
        self.assertContains(response, 'class="custom-admin-sidebar"')
        self.assertContains(response, "Recent Actions")
        self.assertContains(response, reverse("admin:myapp_recent_actions"))
        self.assertNotContains(response, 'id="recent-actions-module"')
        self.assertNotContains(response, 'class="sidebar-recent-actions"')
        self.assertContains(response, 'class="theme-toggle admin-theme-toggle"')
        self.assertContains(response, 'class="admin-profile-menu"')
        self.assertContains(response, "Profile Settings")
        self.assertContains(response, staff_profile_url)
        self.assertContains(response, "Visit Website")
        self.assertContains(response, "Change Password")
        self.assertNotContains(response, "function renderPage(name)")
        self.assertNotContains(response, 'data-page="Customers"')

    def test_admin_login_page_uses_company_logo_layout(self):
        self.client.logout()

        response = self.client.get(reverse("admin:login"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="admin-login-card"')
        self.assertContains(response, 'src="/static/logo.jpeg"')
        self.assertContains(response, "Nanu Investment")
        self.assertContains(response, "Admin Panel")

    def test_login_page_redirects_authenticated_users_by_role(self):
        response = self.client.get(reverse("login"))
        self.assertRedirects(response, reverse("admin:index"))

        customer_user = get_user_model().objects.create_user(
            username="login-customer",
            password="test-password",
        )
        Customer.objects.create(
            user=customer_user,
            first_name="Login",
            last_name="Customer",
            phone_number="9800000099",
            address="Login Road",
        )
        self.client.force_login(customer_user)

        response = self.client.get(reverse("login"))

        self.assertRedirects(response, reverse("customer_dashboard"))

    def test_staff_using_customer_login_redirects_to_admin(self):
        self.client.logout()
        staff_user = get_user_model().objects.create_user(
            username="wrong-login-staff",
            password="test-password",
            is_staff=True,
        )

        response = self.client.post(
            reverse("customer_login"),
            {
                "username": staff_user.username,
                "password": "test-password",
            },
        )

        self.assertRedirects(response, reverse("admin:index"), fetch_redirect_response=False)

    def test_homepage_includes_active_website_popup_content(self):
        WebsitePopup.objects.create(
            title="Important Notice",
            image=ContentFile(b"%PDF-1.4", name="notice.pdf"),
        )

        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Important Notice")
        self.assertContains(response, '"file_type": "pdf"')
        self.assertContains(response, '"pdf_url": "/media/popups/notice')

    def test_site_content_api_includes_active_popup(self):
        WebsitePopup.objects.create(
            title="Important Notice",
            image=ContentFile(b"%PDF-1.4", name="notice.pdf"),
        )

        response = self.client.get(reverse("site_content_api"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["popup"]["title"], "Important Notice")
        self.assertEqual(response.json()["popup"]["file_type"], "pdf")
        self.assertIn("/media/popups/notice", response.json()["popup"]["pdf_url"])
        self.assertTrue(response.json()["popup"]["pdf_url"].endswith(".pdf"))

    def test_reports_page_contains_operational_charts(self):
        response = self.client.get(reverse("admin:myapp_reports"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Reports")
        self.assertContains(response, "Account Type Distribution")
        self.assertContains(response, "Ticket Status")
        self.assertContains(response, "KYC Pie Summary")
        self.assertContains(response, "Staff Collection Graph")

    def test_recent_actions_page_lists_admin_log_entries(self):
        content_type = ContentType.objects.get_for_model(get_user_model())
        LogEntry.objects.log_actions(
            user_id=self.superuser.pk,
            queryset=[self.superuser],
            action_flag=ADDITION,
            change_message="Created test admin",
            single_object=True,
        )

        response = self.client.get(reverse("admin:myapp_recent_actions"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Recent Actions")
        self.assertContains(response, "Action History")
        self.assertContains(response, "Added")
        self.assertContains(response, self.superuser.username)
        self.assertContains(response, content_type.name.title())

    def test_existing_django_model_admin_pages_remain_reachable(self):
        response = self.client.get(reverse("admin:myapp_banner_changelist"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Banners")

    def test_admin_user_change_page_contains_profile_fields(self):
        response = self.client.get(reverse("admin:auth_user_change", args=[self.superuser.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "First name")
        self.assertContains(response, "Last name")
        self.assertContains(response, "Phone number")
        self.assertContains(response, "Address")
        self.assertContains(response, "Photo")
        self.assertContains(response, "Password is hidden for security")
        self.assertContains(response, reverse("admin:auth_user_password_change", args=[self.superuser.pk]))
        self.assertNotContains(response, "algorithm:")
        self.assertNotContains(response, "Raw passwords are not stored")

    def test_profile_is_created_for_new_staff_user(self):
        staff_user = get_user_model().objects.create_user(
            username="staff-admin",
            password="test-password",
            is_staff=True,
        )

        self.assertTrue(AdminProfile.objects.filter(user=staff_user).exists())

    def test_staff_user_can_open_own_profile_without_user_permissions(self):
        staff_user = get_user_model().objects.create_user(
            username="profile-staff",
            password="test-password",
            is_staff=True,
        )
        self.client.force_login(staff_user)

        response = self.client.get(reverse("admin:auth_user_change", args=[staff_user.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "First name")
        self.assertContains(response, "Phone number")
        self.assertContains(response, "Address")
        self.assertContains(response, "Photo")
        self.assertContains(response, 'type="file"')
        self.assertContains(response, reverse("admin:auth_user_password_change", args=[staff_user.pk]))
        self.assertNotContains(response, "Staff status")
        self.assertNotContains(response, "Superuser status")
        self.assertNotContains(response, "Groups")
        self.assertNotContains(response, "User permissions")

    def test_staff_profile_page_recreates_missing_profile_upload_section(self):
        staff_user = get_user_model().objects.create_user(
            username="missing-profile-staff",
            password="test-password",
            is_staff=True,
        )
        AdminProfile.objects.filter(user=staff_user).delete()
        self.client.force_login(staff_user)

        response = self.client.get(reverse("admin:auth_user_change", args=[staff_user.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(AdminProfile.objects.filter(user=staff_user).exists())
        self.assertContains(response, "Photo")
        self.assertContains(response, 'type="file"')

    def test_staff_user_can_upload_photo_from_own_profile_page(self):
        staff_user = get_user_model().objects.create_user(
            username="upload-staff",
            password="test-password",
            is_staff=True,
        )
        self.client.force_login(staff_user)

        response = self.client.get(reverse("admin:myapp_staff_profile_settings"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Profile photo")
        self.assertContains(response, 'type="file"')

        upload = SimpleUploadedFile(
            "staff-profile.png",
            b"\x89PNG\r\n\x1a\n",
            content_type="image/png",
        )
        response = self.client.post(
            reverse("admin:myapp_staff_profile_settings"),
            {
                "phone_number": "9800000001",
                "address": "Staff Road",
                "photo": upload,
            },
            follow=True,
        )
        profile = AdminProfile.objects.get(user=staff_user)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(profile.phone_number, "9800000001")
        self.assertEqual(profile.address, "Staff Road")
        self.assertIn("admin_profiles/staff-profile", profile.photo.name)
        self.assertContains(response, profile.photo.url)

    def test_staff_user_cannot_open_another_user_profile(self):
        staff_user = get_user_model().objects.create_user(
            username="limited-staff",
            password="test-password",
            is_staff=True,
        )
        other_user = get_user_model().objects.create_user(
            username="other-staff",
            password="test-password",
            is_staff=True,
        )
        self.client.force_login(staff_user)

        response = self.client.get(reverse("admin:auth_user_change", args=[other_user.pk]))

        self.assertEqual(response.status_code, 403)

    def test_customer_kyc_admin_page_and_approval_flow(self):
        customer = Customer.objects.create(
            first_name="Ram",
            last_name="Sah",
            phone_number="9800000000",
            address="Main Road",
            citizenship_number="CTZ-001",
            opening_balance=1000,
        )

        response = self.client.get(reverse("admin:myapp_customer_changelist"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Customers &amp; KYC")
        self.assertContains(response, "Ram Sah")
        self.assertContains(response, "Send selected customers for KYC approval")

        response = self.client.post(
            reverse("admin:myapp_customer_changelist"),
            {
                "action": "send_for_kyc_approval",
                "_selected_action": [customer.pk],
                "index": 0,
            },
            follow=True,
        )
        customer.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(customer.kyc_status, Customer.KycStatus.PENDING)
        self.assertIsNotNone(customer.submitted_for_approval_at)

    def test_daily_collections_admin_lists_customers(self):
        customer = Customer.objects.create(
            first_name="Sita",
            last_name="Devi",
            phone_number="9811111111",
            address="Ward 03",
            citizenship_number="CTZ-DAILY-01",
            opening_balance=500,
        )

        response = self.client.get(reverse("admin:myapp_dailycollection_changelist"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Daily Collections")
        self.assertContains(response, "Sita Devi")
        self.assertContains(response, "9811111111")
        self.assertContains(response, "CTZ-DAILY-01")
        self.assertContains(response, "Add Collection")
        self.assertContains(response, reverse("admin:myapp_dailycollection_collect", args=[customer.pk]))

        for search_value in ("Sita Devi", "9811111111", customer.customer_id, "CTZ-DAILY-01"):
            with self.subTest(search_value=search_value):
                search_response = self.client.get(
                    reverse("admin:myapp_dailycollection_changelist"),
                    {"q": search_value},
                )
                self.assertContains(search_response, "Sita Devi")

        missing_response = self.client.get(
            reverse("admin:myapp_dailycollection_changelist"),
            {"q": "UNKNOWN-CUSTOMER"},
        )
        self.assertContains(missing_response, "Customer does not exist")

    def test_daily_collection_entry_shows_account_and_saves_new_amount(self):
        customer = Customer.objects.create(
            first_name="Collection",
            last_name="Account",
            phone_number="9811111122",
            address="Collection Road",
            citizenship_number="CTZ-COLLECT-02",
            opening_balance=Decimal("500.00"),
        )
        CollectionRecord.objects.create(
            customer=customer,
            collected_by=self.superuser,
            amount=Decimal("75.50"),
            visit_type=CollectionRecord.VisitType.SHOP,
            collected_at=timezone.now(),
            note="First visit",
        )
        collect_url = reverse("admin:myapp_dailycollection_collect", args=[customer.pk])

        response = self.client.get(collect_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Collection Account")
        self.assertContains(response, customer.customer_id)
        self.assertContains(response, "CTZ-COLLECT-02")
        self.assertContains(response, "New amount collected")
        self.assertEqual(response.context["collected_total"], Decimal("75.50"))
        self.assertEqual(response.context["account_total"], Decimal("575.50"))

        response = self.client.post(
            collect_url,
            {
                "amount": "24.50",
                "visit_type": CollectionRecord.VisitType.HOME,
                "note": "Collected from home",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        new_collection = CollectionRecord.objects.get(note="Collected from home")
        transaction = new_collection.transaction
        self.assertEqual(new_collection.customer, customer)
        self.assertEqual(new_collection.collected_by, self.superuser)
        self.assertEqual(new_collection.amount, Decimal("24.50"))
        self.assertEqual(transaction.customer, customer)
        self.assertEqual(transaction.amount, Decimal("24.50"))
        self.assertEqual(transaction.balance_after, Decimal("600.00"))
        self.assertEqual(transaction.payment_method, "Cash")
        self.assertContains(response, transaction.transaction_id)
        self.assertContains(response, "Print Bill")
        self.assertContains(response, "Download PDF")
        self.assertContains(response, "Download JPG")

    def test_transaction_section_lists_receipts_and_downloads_bill(self):
        customer = Customer.objects.create(
            first_name="Bill",
            last_name="Customer",
            phone_number="9811111133",
            address="Bill Road",
            opening_balance=Decimal("300.00"),
        )
        collection = CollectionRecord.objects.create(
            customer=customer,
            collected_by=self.superuser,
            amount=Decimal("45.00"),
            visit_type=CollectionRecord.VisitType.OFFICE,
            collected_at=timezone.now(),
            note="Office payment",
        )
        transaction = Transaction.objects.create(
            collection_record=collection,
            customer=customer,
            amount=collection.amount,
            balance_after=Decimal("345.00"),
            payment_method="Cash",
            visit_type=collection.visit_type,
            collected_by=self.superuser,
            note=collection.note,
            transacted_at=collection.collected_at,
        )

        response = self.client.get(reverse("admin:myapp_transaction_changelist"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, transaction.transaction_id)
        self.assertContains(response, "Print")
        self.assertContains(response, "PDF")
        self.assertContains(response, "JPG")

        receipt_response = self.client.get(reverse("admin:myapp_transaction_receipt", args=[transaction.pk]))
        self.assertEqual(receipt_response.status_code, 200)
        self.assertContains(receipt_response, "Collection Transaction Bill")
        self.assertContains(receipt_response, "Bill Customer")
        self.assertContains(receipt_response, "Rs 45.00")
        self.assertContains(receipt_response, "Download PDF")
        self.assertContains(receipt_response, "Download JPG")

        pdf_response = self.client.get(reverse("admin:myapp_transaction_download_pdf", args=[transaction.pk]))
        self.assertEqual(pdf_response.status_code, 200)
        self.assertEqual(pdf_response["Content-Type"], "application/pdf")
        self.assertEqual(pdf_response["Content-Disposition"], f'attachment; filename="{transaction.transaction_id}.pdf"')
        self.assertTrue(pdf_response.content.startswith(b"%PDF"))

        jpg_response = self.client.get(reverse("admin:myapp_transaction_download_jpg", args=[transaction.pk]))
        self.assertEqual(jpg_response.status_code, 200)
        self.assertEqual(jpg_response["Content-Type"], "image/jpeg")
        self.assertEqual(jpg_response["Content-Disposition"], f'attachment; filename="{transaction.transaction_id}.jpg"')
        self.assertTrue(jpg_response.content.startswith(b"\xff\xd8\xff"))

    def test_accounting_page_shows_transaction_vouchers(self):
        customer = Customer.objects.create(
            first_name="Accounting",
            last_name="Customer",
            phone_number="9811111144",
            address="Accounting Road",
            opening_balance=Decimal("1000.00"),
        )
        collection = CollectionRecord.objects.create(
            customer=customer,
            collected_by=self.superuser,
            amount=Decimal("250.00"),
            visit_type=CollectionRecord.VisitType.OFFICE,
            collected_at=timezone.now(),
            note="Accounting collection",
        )
        transaction = Transaction.objects.create(
            collection_record=collection,
            customer=customer,
            amount=collection.amount,
            balance_after=Decimal("1250.00"),
            payment_method="Cash",
            visit_type=collection.visit_type,
            collected_by=self.superuser,
            note=collection.note,
            transacted_at=collection.collected_at,
        )

        response = self.client.get(reverse("admin:myapp_accounting"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Accounting")
        self.assertContains(response, "Income This Month")
        self.assertContains(response, "Net Surplus")
        self.assertContains(response, transaction.transaction_id)
        self.assertContains(response, "Collection from Accounting Customer")
        self.assertContains(response, "Rs 250.00")

        dashboard_response = self.client.get(reverse("admin:index"))
        self.assertContains(dashboard_response, reverse("admin:myapp_accounting"))

    def test_approvals_page_lists_and_processes_pending_requests(self):
        customer = Customer.objects.create(
            first_name="Approval",
            last_name="Customer",
            phone_number="9811111155",
            address="Approval Road",
            kyc_status=Customer.KycStatus.PENDING,
            submitted_for_approval_at=timezone.now(),
        )
        ticket = Ticket.objects.create(
            title="Verify completed work",
            description="Staff has completed this request.",
            customer=customer,
            created_by=self.superuser,
            assigned_to=self.superuser,
            status=Ticket.Status.STAFF_COMPLETED,
            staff_completed_at=timezone.now(),
        )

        response = self.client.get(reverse("admin:myapp_approvals"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "KYC Approval Requests")
        self.assertContains(response, "Ticket Completion Requests")
        self.assertContains(response, "Approval Customer")
        self.assertContains(response, "Verify completed work")

        response = self.client.post(
            reverse("admin:myapp_approvals"),
            {"action": "approve_kyc", "object_id": customer.pk},
            follow=True,
        )
        customer.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(customer.kyc_status, Customer.KycStatus.APPROVED)
        self.assertEqual(customer.approved_by, self.superuser)
        self.assertIsNotNone(customer.approved_at)

        response = self.client.post(
            reverse("admin:myapp_approvals"),
            {"action": "verify_ticket", "object_id": ticket.pk},
            follow=True,
        )
        ticket.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ticket.status, Ticket.Status.VERIFIED_COMPLETED)
        self.assertEqual(ticket.verified_by, self.superuser)
        self.assertIsNotNone(ticket.verified_at)

        dashboard_response = self.client.get(reverse("admin:index"))
        self.assertContains(dashboard_response, reverse("admin:myapp_approvals"))

    def test_manual_collection_datetime_is_counted_and_sent_for_approval(self):
        customer = Customer.objects.create(
            first_name="Manual",
            last_name="Collection",
            phone_number="9811111166",
            address="Manual Road",
            opening_balance=Decimal("1000.00"),
        )
        manual_collected_at = timezone.localtime(timezone.now() - timedelta(days=2)).replace(second=0, microsecond=0)
        collect_url = reverse("admin:myapp_dailycollection_collect", args=[customer.pk])

        response = self.client.post(
            collect_url,
            {
                "amount": "150.00",
                "visit_type": CollectionRecord.VisitType.SHOP,
                "use_manual_collected_at": "on",
                "manual_collected_at": manual_collected_at.strftime("%Y-%m-%dT%H:%M"),
                "note": "Manual date request",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        collection = CollectionRecord.objects.get(note="Manual date request")
        self.assertEqual(collection.amount, Decimal("150.00"))
        self.assertTrue(collection.collected_at_was_manual)
        self.assertEqual(collection.datetime_approval_status, CollectionRecord.DateTimeApprovalStatus.PENDING)
        self.assertIsNotNone(collection.datetime_approval_requested_at)
        self.assertEqual(collection.transaction.amount, Decimal("150.00"))
        self.assertEqual(collection.transaction.balance_after, Decimal("1150.00"))

        approvals_response = self.client.get(reverse("admin:myapp_approvals"))
        self.assertContains(approvals_response, "Manual Collection Date/Time Requests")
        self.assertContains(approvals_response, "Manual Collection")
        self.assertContains(approvals_response, "Rs 150.00")

        response = self.client.post(
            reverse("admin:myapp_approvals"),
            {"action": "approve_collection_datetime", "object_id": collection.pk},
            follow=True,
        )
        collection.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(collection.datetime_approval_status, CollectionRecord.DateTimeApprovalStatus.APPROVED)
        self.assertEqual(collection.datetime_approved_by, self.superuser)
        self.assertIsNotNone(collection.datetime_approved_at)

    def test_online_collection_requires_reference_and_stores_receipt(self):
        customer = Customer.objects.create(
            first_name="Online",
            last_name="Payment",
            phone_number="9811111177",
            address="Online Road",
            opening_balance=Decimal("700.00"),
        )
        collect_url = reverse("admin:myapp_dailycollection_collect", args=[customer.pk])

        missing_reference_response = self.client.post(
            collect_url,
            {
                "amount": "80.00",
                "visit_type": CollectionRecord.VisitType.OFFICE,
                "payment_method": CollectionRecord.PaymentMethod.ONLINE,
                "note": "Missing online reference",
            },
        )

        self.assertEqual(missing_reference_response.status_code, 200)
        self.assertContains(missing_reference_response, "Enter the online reference number or transaction ID.")

        receipt = SimpleUploadedFile("receipt.jpg", b"receipt-proof", content_type="image/jpeg")
        response = self.client.post(
            collect_url,
            {
                "amount": "80.00",
                "visit_type": CollectionRecord.VisitType.OFFICE,
                "payment_method": CollectionRecord.PaymentMethod.ONLINE,
                "payment_reference": "ESEWA-12345",
                "payment_receipt": receipt,
                "note": "Online payment",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        collection = CollectionRecord.objects.get(note="Online payment")
        transaction = collection.transaction
        self.assertEqual(collection.payment_method, CollectionRecord.PaymentMethod.ONLINE)
        self.assertEqual(collection.payment_reference, "ESEWA-12345")
        self.assertTrue(collection.payment_receipt.name)
        self.assertEqual(transaction.payment_method, "Online")
        self.assertEqual(transaction.payment_reference, "ESEWA-12345")
        self.assertTrue(transaction.payment_receipt.name)
        self.assertContains(response, "ESEWA-12345")

    def test_customer_form_contains_add_document_inline(self):
        response = self.client.get(reverse("admin:myapp_customer_add"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "KYC Documents")
        self.assertContains(response, "Document type")
        self.assertContains(response, "Document name")
        self.assertContains(response, "Add another KYC Document")

    def test_customer_can_have_multiple_named_kyc_documents(self):
        customer = Customer.objects.create(
            first_name="Document",
            last_name="Holder",
            phone_number="9822222222",
            address="Document Road",
        )
        CustomerKYCDocument.objects.create(
            customer=customer,
            document_type=CustomerKYCDocument.DocumentType.CITIZENSHIP_FRONT,
            document_name="Citizenship front side",
            document="customer_kyc/front.pdf",
        )
        CustomerKYCDocument.objects.create(
            customer=customer,
            document_type=CustomerKYCDocument.DocumentType.ADDRESS_PROOF,
            document_name="Electricity bill",
            document="customer_kyc/address.pdf",
        )

        self.assertEqual(customer.kyc_documents.count(), 2)

    def test_admin_customer_add_creates_customer_login(self):
        response = self.client.post(
            reverse("admin:myapp_customer_add"),
            {
                "first_name": "Auto",
                "last_name": "Login",
                "phone_number": "9855555555",
                "email": "auto-login@example.com",
                "address": "Auto Login Road",
                "account_type": Customer.AccountType.SAVINGS,
                "opening_balance": "500.00",
                "kyc_status": Customer.KycStatus.APPROVED,
                "kyc_documents-TOTAL_FORMS": "0",
                "kyc_documents-INITIAL_FORMS": "0",
                "kyc_documents-MIN_NUM_FORMS": "0",
                "kyc_documents-MAX_NUM_FORMS": "1000",
            },
            follow=True,
        )
        customer = Customer.objects.get(phone_number="9855555555")

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(customer.user)
        self.assertEqual(customer.user.username, customer.customer_id.lower())
        self.assertFalse(customer.user.is_staff)
        self.assertFalse(customer.user.is_superuser)
        credential = customer.ebanking_credential
        self.assertEqual(credential.username, customer.customer_id.lower())
        self.assertTrue(credential.temporary_password)
        self.assertContains(response, "Customer login created.")
        self.assertContains(response, "Password:")

        response = self.client.get(reverse("admin:myapp_customer_change", args=[customer.pk]))
        self.assertContains(response, "Profile photo")

    def test_customer_portal_shows_own_account_and_creates_ticket(self):
        customer_user = get_user_model().objects.create_user(
            username="customer-user",
            password="test-password",
        )
        customer = Customer.objects.create(
            user=customer_user,
            first_name="Portal",
            last_name="Customer",
            phone_number="9844444444",
            address="Portal Road",
            opening_balance=Decimal("1200.00"),
            kyc_status=Customer.KycStatus.APPROVED,
        )
        CollectionRecord.objects.create(
            customer=customer,
            collected_by=self.superuser,
            amount=Decimal("80.00"),
            visit_type=CollectionRecord.VisitType.OFFICE,
            collected_at=timezone.now(),
        )

        self.client.logout()
        self.assertTrue(self.client.login(username="customer-user", password="test-password"))

        admin_response = self.client.get(reverse("admin:index"))
        self.assertEqual(admin_response.status_code, 302)

        response = self.client.get(reverse("customer_dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Portal Customer")
        self.assertContains(response, customer.customer_id)
        self.assertContains(response, "Rs 1280.00")

        response = self.client.post(
            reverse("customer_create_ticket"),
            {
                "title": "Need account statement",
                "description": "Please provide my latest statement.",
                "priority": Ticket.Priority.NORMAL,
            },
            follow=True,
        )
        ticket = Ticket.objects.get(title="Need account statement")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ticket.customer, customer)
        self.assertEqual(ticket.created_by, customer_user)
        self.assertEqual(ticket.status, Ticket.Status.OPEN)

    def test_customer_can_upload_own_profile_photo(self):
        customer_user = get_user_model().objects.create_user(
            username="photo-customer",
            password="test-password",
        )
        customer = Customer.objects.create(
            user=customer_user,
            first_name="Photo",
            last_name="Customer",
            phone_number="9844444477",
            address="Photo Road",
        )

        self.client.logout()
        self.assertTrue(self.client.login(username="photo-customer", password="test-password"))

        response = self.client.get(reverse("customer_profile_settings"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Profile photo")

        upload = SimpleUploadedFile(
            "profile.png",
            b"\x89PNG\r\n\x1a\n",
            content_type="image/png",
        )
        response = self.client.post(
            reverse("customer_profile_settings"),
            {"profile_photo": upload},
            follow=True,
        )
        customer.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertIn("customer_profiles/profile", customer.profile_photo.name)
        self.assertContains(response, customer.profile_photo.url)

    def test_customer_can_change_own_password(self):
        customer_user = get_user_model().objects.create_user(
            username="password-customer",
            password="OldPass@123",
        )
        Customer.objects.create(
            user=customer_user,
            first_name="Password",
            last_name="Customer",
            phone_number="9844444455",
            address="Password Road",
        )
        self.client.logout()
        self.assertTrue(self.client.login(username="password-customer", password="OldPass@123"))

        response = self.client.post(
            reverse("customer_change_password"),
            {
                "old_password": "OldPass@123",
                "new_password1": "NewPass@12345",
                "new_password2": "NewPass@12345",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.client.logout()
        self.assertTrue(self.client.login(username="password-customer", password="NewPass@12345"))
        credential = EBankingCredential.objects.get(user=customer_user)
        self.assertEqual(credential.temporary_password, "")
        self.assertIsNotNone(credential.password_changed_at)

    def test_admin_can_reset_customer_password(self):
        customer_user = get_user_model().objects.create_user(
            username="reset-customer",
            password="OldPass@123",
        )
        customer = Customer.objects.create(
            user=customer_user,
            first_name="Reset",
            last_name="Customer",
            phone_number="9844444466",
            address="Reset Road",
        )

        response = self.client.post(
            reverse("admin:myapp_customer_reset_password", args=[customer.pk]),
            {
                "new_password1": "ResetPass@12345",
                "new_password2": "ResetPass@12345",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        credential = EBankingCredential.objects.get(customer=customer)
        self.assertEqual(credential.temporary_password, "ResetPass@12345")
        self.client.logout()
        self.assertTrue(self.client.login(username="reset-customer", password="ResetPass@12345"))

    def test_ebanking_admin_lists_customer_credentials(self):
        customer_user = get_user_model().objects.create_user(
            username="ebanking-customer",
            password="TempPass@123",
        )
        customer = Customer.objects.create(
            user=customer_user,
            first_name="Ebanking",
            last_name="Customer",
            phone_number="9844444477",
            email="ebanking@example.com",
            address="Ebanking Road",
        )
        EBankingCredential.objects.create(
            customer=customer,
            user=customer_user,
            username="ebanking-customer",
            temporary_password="TempPass@123",
        )

        response = self.client.get(reverse("admin:myapp_ebankingcredential_changelist"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ebanking Customer")
        self.assertContains(response, "9844444477")
        self.assertContains(response, "ebanking@example.com")
        self.assertContains(response, "ebanking-customer")
        self.assertContains(response, "TempPass@123")
        self.assertContains(response, "Send Email")
        self.assertContains(response, "Send SMS")
        self.assertContains(response, "Call")

    def test_ticket_admin_assignment_completion_and_verification_flow(self):
        staff_user = get_user_model().objects.create_user(
            username="ticket-staff",
            password="test-password",
            is_staff=True,
        )
        ticket = Ticket.objects.create(
            title="Fix customer KYC",
            description="Customer document needs review.",
            created_by=self.superuser,
            assigned_to=staff_user,
            status=Ticket.Status.ASSIGNED,
        )

        response = self.client.get(reverse("admin:myapp_ticket_changelist"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Fix customer KYC")
        self.assertContains(response, "Mark selected tickets complete as staff")
        self.assertContains(response, "Admin verify selected tickets as completed")

        response = self.client.post(
            reverse("admin:myapp_ticket_changelist"),
            {
                "action": "mark_tickets_staff_completed",
                "_selected_action": [ticket.pk],
                "index": 0,
            },
            follow=True,
        )
        ticket.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ticket.status, Ticket.Status.STAFF_COMPLETED)
        self.assertIsNotNone(ticket.staff_completed_at)

        ticket.admin_verification_reason = "Work checked and accepted."
        ticket.save(update_fields=["admin_verification_reason"])
        response = self.client.post(
            reverse("admin:myapp_ticket_changelist"),
            {
                "action": "verify_tickets_completed",
                "_selected_action": [ticket.pk],
                "index": 0,
            },
            follow=True,
        )
        ticket.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ticket.status, Ticket.Status.VERIFIED_COMPLETED)
        self.assertEqual(ticket.verified_by, self.superuser)
        self.assertIsNotNone(ticket.verified_at)

    def test_customer_delete_moves_record_to_recycle_bin_and_restores_it(self):
        customer = Customer.objects.create(
            first_name="Recycle",
            last_name="Customer",
            phone_number="9833333333",
            address="Archive Road",
        )

        customer.delete(deleted_by=self.superuser)

        self.assertFalse(Customer.objects.filter(pk=customer.pk).exists())
        self.assertTrue(Customer.all_objects.filter(pk=customer.pk, is_deleted=True).exists())
        recycle_item = RecycleBinItem.objects.get(object_id=customer.pk)
        self.assertEqual(recycle_item.deleted_by, self.superuser)

        self.assertTrue(recycle_item.restore_object())
        self.assertTrue(Customer.objects.filter(pk=customer.pk).exists())
        self.assertFalse(RecycleBinItem.objects.filter(pk=recycle_item.pk).exists())

    def test_archived_customer_number_is_not_reused(self):
        archived_customer = Customer.objects.create(
            first_name="Archived",
            last_name="Number",
            phone_number="9800000010",
            address="Number Road",
        )
        archived_customer.delete(deleted_by=self.superuser)

        new_customer = Customer.objects.create(
            first_name="New",
            last_name="Number",
            phone_number="9800000011",
            address="Number Road",
        )

        self.assertNotEqual(new_customer.customer_id, archived_customer.customer_id)

    def test_admin_user_delete_deactivates_and_hides_user_until_restored(self):
        staff_user = get_user_model().objects.create_user(
            username="recycled-staff",
            password="test-password",
            is_staff=True,
        )

        response = self.client.post(
            reverse("admin:auth_user_changelist"),
            {
                "action": "move_selected_to_recycle_bin",
                "_selected_action": [staff_user.pk],
                "index": 0,
            },
            follow=True,
        )
        staff_user.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertFalse(staff_user.is_active)
        self.assertNotContains(response, "recycled-staff")
        recycle_item = RecycleBinItem.objects.get(object_id=staff_user.pk)

        self.assertTrue(recycle_item.restore_object())
        staff_user.refresh_from_db()
        self.assertTrue(staff_user.is_active)

    def test_recycle_bin_requires_confirmation_before_permanent_delete(self):
        customer = Customer.objects.create(
            first_name="Permanent",
            last_name="Delete",
            phone_number="9844444444",
            address="Final Road",
        )
        customer.delete(deleted_by=self.superuser)
        recycle_item = RecycleBinItem.objects.get(object_id=customer.pk)

        response = self.client.post(
            reverse("admin:myapp_recyclebinitem_changelist"),
            {
                "action": "permanently_delete_selected",
                "_selected_action": [recycle_item.pk],
                "index": 0,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Permanent deletion cannot be undone")
        self.assertTrue(Customer.all_objects.filter(pk=customer.pk).exists())

        response = self.client.post(
            reverse("admin:myapp_recyclebinitem_changelist"),
            {
                "action": "permanently_delete_selected",
                "_selected_action": [recycle_item.pk],
                "confirm_permanent": "yes",
                "select_across": "0",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Customer.all_objects.filter(pk=customer.pk).exists())
        self.assertFalse(RecycleBinItem.objects.filter(pk=recycle_item.pk).exists())
