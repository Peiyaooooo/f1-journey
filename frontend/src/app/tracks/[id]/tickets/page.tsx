import { fetchCircuit, fetchCircuitTickets, fetchUnmatchedTickets } from "@/lib/api";
import TicketTable from "@/components/TicketTable";
import Link from "next/link";
import { notFound } from "next/navigation";

export default async function TicketComparisonPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const circuitId = parseInt(id, 10);
  if (isNaN(circuitId)) notFound();

  let circuit;
  try {
    circuit = await fetchCircuit(circuitId);
  } catch {
    notFound();
  }

  const [tickets, unmatchedTickets] = await Promise.all([
    fetchCircuitTickets(circuitId).catch(() => []),
    fetchUnmatchedTickets(circuitId).catch(() => []),
  ]);

  return (
    <div>
      <div className="px-6 py-6 border-b border-gray-800">
        <Link href={`/tracks/${circuitId}`} className="text-sm text-gray-400 hover:text-white">
          &larr; Back to {circuit.name}
        </Link>
        <h1 className="text-2xl font-bold mt-2">Ticket Comparison — {circuit.name}</h1>
        <p className="text-gray-400 text-sm">Compare ticket prices across all sources</p>
      </div>

      <div className="px-6 py-6">
        <h2 className="text-lg font-bold mb-4">All Tickets ({tickets.length})</h2>
        <TicketTable tickets={tickets} />
      </div>

      {unmatchedTickets.length > 0 && (
        <div className="px-6 py-6 border-t border-gray-800">
          <h2 className="text-lg font-bold mb-4">Other Tickets ({unmatchedTickets.length})</h2>
          <p className="text-sm text-gray-400 mb-4">These tickets could not be matched to a specific seat section</p>
          <TicketTable tickets={unmatchedTickets} />
        </div>
      )}
    </div>
  );
}
