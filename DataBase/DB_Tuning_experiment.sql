-- # 실험 1
-- explain 
-- select * from product where category = '하의'; 

-- explain analyze
-- select * from product where category = '하의';  

-- CREATE INDEX idx_product_category ON product(category);

-- DROP INDEX idx_product_category ON product;

-- # 실험 2
-- explain
-- select * from product where price >= 100000;

-- explain analyze
-- select * from product where price >= 100000;

-- create index idx_product_price on product(price);

-- drop index idx_product_price on product;

-- # 실험 3
-- explain
-- select orders.order_id, orders.customer_id, order_date, option_id, quantity, unit_price from orders
-- inner join order_detail on orders.order_id = order_detail.order_id
-- where customer_id = 32563 order by orders.order_date;

-- explain analyze
-- select orders.order_id, orders.customer_id, order_date, option_id, quantity, unit_price from orders
-- inner join order_detail on orders.order_id = order_detail.order_id
-- where customer_id = 32563 order by orders.order_date;

-- show index from orders;
-- show index from order_detail;

-- CREATE INDEX idx_orders_customer_date
-- ON orders(customer_id, order_date);

-- drop index idx_orders_customer_date on orders;