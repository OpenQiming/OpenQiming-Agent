from flask_login import UserMixin
from sqlalchemy import Column, String, DateTime, text, PrimaryKeyConstraint, Index

from agent_platform_basic.extensions.ext_database import Base
from agent_platform_basic.extensions.ext_database import db
from agent_platform_common.configs import agent_platform_config
from .tenant_account_join import TenantAccountJoin
from .account_intergrate import AccountIntegrate
from .tenant import Tenant
from .string_uuid import StringUUID
from agent_platform_basic.models.enum_model.account import AccountStatus
from agent_platform_basic.models.enum_model.tenant import TenantAccountRole

"""

@Date    ：2024/7/13 9:55 
@Version: 1.0
@Description:
    用户实体
"""


class Account(UserMixin, Base):
    __tablename__ = 'accounts'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='account_pkey'),
        Index('account_email_idx', 'email'),
        Index('account_mobile_idx', 'mobile')
    )

    id = Column(StringUUID, server_default=text('uuid_generate_v4()'))
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    password = Column(String(255), nullable=True)
    password_salt = Column(String(255), nullable=True)
    avatar = Column(String(255))
    interface_language = Column(String(255))
    interface_theme = Column(String(255))
    timezone = Column(String(255))
    last_login_at = Column(DateTime)
    last_login_ip = Column(String(255))
    last_active_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))
    status = Column(String(16), nullable=False, server_default=text("'active'::character varying"))
    initialized_at = Column(DateTime)
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))
    updated_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))
    employee_number = Column(String(255))
    username = Column(String(255))
    mobile = Column(String(255))
    company_name = Column(String(255))
    province = Column(String(255))
    first_level_company = Column(String(255))
    second_level_company = Column(String(255))

    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'interface_language': self.interface_language,
            # 'interface_theme': self.interface_theme,
            'timezone': self.timezone,
            'status': self.status,
            'employee_number': self.employee_number
        }

    @property
    def is_password_set(self):
        return self.password is not None

    @property
    def tenants(self):
        return self._tenants

    @property
    def roles(self):
        return self._roles

    @property
    def current_tenant(self):
        return self._current_tenant

    @current_tenant.setter
    def current_tenant(self, value):
        tenant = value
        ta = db.session.query(TenantAccountJoin).filter_by(tenant_id=tenant.id, account_id=self.id).first()
        if ta:
            tenant.current_role = ta.role
        else:
            tenant = None
        self._current_tenant = tenant

    @property
    def current_tenant_id(self):
        return self._current_tenant.id

    @current_tenant_id.setter
    def current_tenant_id(self, value):
        try:
            tenant_account_join = db.session.query(Tenant, TenantAccountJoin) \
                .filter(Tenant.id == value) \
                .filter(TenantAccountJoin.tenant_id == Tenant.id) \
                .filter(TenantAccountJoin.account_id == self.id) \
                .one_or_none()

            if tenant_account_join:
                tenant, ta = tenant_account_join
                tenant.current_role = ta.role
            else:
                tenant = None
        except:
            tenant = None

        self._current_tenant = tenant

    def get_status(self) -> AccountStatus:
        status_str = self.status
        return AccountStatus(status_str)

    @classmethod
    def get_by_openid(cls, provider: str, open_id: str) -> db.Model:
        account_integrate = db.session.query(AccountIntegrate). \
            filter(AccountIntegrate.provider == provider, AccountIntegrate.open_id == open_id). \
            one_or_none()
        if account_integrate:
            return db.session.query(Account). \
                filter(Account.id == account_integrate.account_id). \
                one_or_none()
        return None

    def get_integrates(self) -> list[db.Model]:
        ai = db.Model
        return db.session.query(ai).filter(
            ai.account_id == self.id
        ).all()

    # check current_user.current_tenant.current_role in ['admin', 'owner']
    @property
    def is_admin_or_owner(self):
        return TenantAccountRole.is_privileged_role(self._current_tenant.current_role)

    @property
    def is_editor(self):
        return TenantAccountRole.is_editing_role(self._current_tenant.current_role)

    def is_tenant_admin_or_owner(self, tenant_id: str):
        return TenantAccountRole.is_privileged_role(self.roles.get(tenant_id))

    def is_tenant_editor(self, tenant_id: str):
        return TenantAccountRole.is_editing_role(self.roles.get(tenant_id))

    def is_tenant_user(self, tenant_id: str):
        if tenant_id == agent_platform_config.GLOBAL_TENANT_ID:
            return True
        return TenantAccountRole.is_valid_role(self.roles.get(tenant_id))

    def is_tenant_owner(self, tenant_id: str):
        return TenantAccountRole.is_owner_role(self.roles.get(tenant_id))

    def is_super(self):
        return self.employee_number == '00000000'
        # return self.id == "030a553f-d29d-4ec4-8bab-722371e302ac"
        # return self.id == f"{'1'*8}-{'1'*4}-{'1'*4}-{'1'*12}"
