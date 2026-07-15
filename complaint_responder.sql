create database ai_complaint_responder;
use ai_complaint_responder;

create table complaints(
	Id INT AUTO_INCREMENT PRIMARY KEY,
    Customer_name TEXT NOT NULL,
    Customer_email TEXT NOT NULL,
    Complaint_text TEXT NOT NULL,
    Predicted_category VARCHAR(100),
    Auto_response TEXT,
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
ALTER TABLE complaints
ADD COLUMN Complaint_status VARCHAR(50) DEFAULT 'Pending',
ADD COLUMN Followup TEXT,
ADD COLUMN Admin_note TEXT;

desc complaints;

select * from complaints;
select DISTINCT(Predicted_category) from complaints;
select* from customers;

SELECT Complaint_status FROM complaints
WHERE C_id = 1003
ORDER BY Timestamp DESC
LIMIT 1;

update complaints set Predicted_category = "Customer Support" where Predicted_category = "Customer Service";


-- Technical Issue', 'Payment Issue', 'Account Issue',
   --     'Delivery Delay', 'Service Issue', 'Product Damage',
      --  'Login Trouble', 'App Bug', 'Wrong Item', 'Customer Support'
      
      select * from complaints where Predicted_category="Customer support";