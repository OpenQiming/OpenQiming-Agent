from agent_platform_basic.extensions.ext_database import db
from agent_platform_basic.models.db_model import StringUUID
""" 
@Date    ：2024/7/14 22:05 
@Version: 1.0
@Description:

"""

class ProviderOrder(db.Model):
    __tablename__ = 'provider_orders'
    __table_args__ = (
        db.PrimaryKeyConstraint('id', name='provider_order_pkey'),
        db.Index('provider_order_tenant_provider_idx', 'tenant_id', 'provider_name'),
    )

    id = db.Column(StringUUID, server_default=db.text('uuid_generate_v4()'))
    tenant_id = db.Column(StringUUID, nullable=False)
    provider_name = db.Column(db.String(255), nullable=False)
    account_id = db.Column(StringUUID, nullable=False)
    payment_product_id = db.Column(db.String(191), nullable=False)
    payment_id = db.Column(db.String(191))
    transaction_id = db.Column(db.String(191))
    quantity = db.Column(db.Integer, nullable=False, server_default=db.text('1'))
    currency = db.Column(db.String(40))
    total_amount = db.Column(db.Integer)
    payment_status = db.Column(db.String(40), nullable=False, server_default=db.text("'wait_pay'::character varying"))
    paid_at = db.Column(db.DateTime)
    pay_failed_at = db.Column(db.DateTime)
    refunded_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))
