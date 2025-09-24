import RequestRepoForm from "@/components/RequestRepoForm";
import Image from "next/image";
import { Feedback } from "../components/Feedback";
import { DESCRIPTION, TITLE } from "./stringAssets";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-gray-100 p-4">
      <div className="mb-8">
        <Image
          className="rounded-md"
          src="/logo.webp"
          alt="Logo"
          width={200}
          height={200}
        />
      </div>
      <h1 className="text-3xl font-bold text-center text-gray-800 mb-6">
        {TITLE}
      </h1>
      <p className="text-lg text-center text-gray-600 mb-8 max-w-lg">
        {DESCRIPTION}
      </p>

      <RequestRepoForm />

      <div className="flex flex-col items-center">
        <Feedback />
      </div>
    </main>
  );
}
