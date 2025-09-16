import React, { useEffect, useState } from "react";

function InvoiceList() {
  const [invoices, setInvoices] = useState([]);
  const [selectedInvoice, setSelectedInvoice] = useState(null);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/invoices")
      .then((res) => res.json())
      .then((data) => setInvoices(data))
      .catch((err) => console.error("Failed to load invoices:", err));
  }, []);

  return (
    <div className="p-4 max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold mb-4">Saved Invoices</h2>
      <div className="flex gap-6">
        <ul className="w-1/3 border rounded p-2 max-h-[400px] overflow-auto">
          {invoices.length === 0 && <p>No invoices found.</p>}
          {invoices.map((inv) => (
            <li
              key={inv._id}
              className="cursor-pointer p-2 hover:bg-gray-100"
              onClick={() => setSelectedInvoice(inv)}
            >
              Invoice #: {inv.invoice_number || "N/A"}
            </li>
          ))}
        </ul>
        <div className="w-2/3 p-4 border rounded max-h-[400px] overflow-auto">
          {selectedInvoice ? (
            <>
              <h3 className="font-semibold text-xl mb-2">Invoice Details:</h3>
              <pre>{JSON.stringify(selectedInvoice, null, 2)}</pre>
            </>
          ) : (
            <p>Select an invoice to view details</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default InvoiceList;
