import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { FileText, Quote } from "lucide-react"

export default function Citations() {
  const citations = props.citations || []

  if (citations.length === 0) {
    return null
  }

  return (
    <Card className="w-full mt-4">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-sm font-medium">
          <FileText className="h-4 w-4" />
          Citas y fuentes ({citations.length})
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Accordion type="single" collapsible className="w-full">
          {citations.map((citation, index) => {
            const textoCitado = citation.texto_citado || ""
            const spanStart = citation.span_start || 0
            const spanEnd = citation.span_end || 0
            const referencias = citation.referencias || []
            
            return (
              <AccordionItem key={index} value={`item-${index}`}>
                <AccordionTrigger className="text-left">
                  <div className="flex flex-col items-start gap-1 w-full">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold">Cita #{citation.citation_index || index + 1}</span>
                      <Badge variant="secondary" className="text-xs">
                        {referencias.length} {referencias.length === 1 ? 'fuente' : 'fuentes'}
                      </Badge>
                    </div>
                    {textoCitado && (
                      <span className="text-sm text-muted-foreground italic truncate w-full">
                        "{textoCitado.substring(0, 80)}{textoCitado.length > 80 ? '...' : ''}"
                      </span>
                    )}
                  </div>
                </AccordionTrigger>
                <AccordionContent>
                  <div className="space-y-4 pt-2">
                    {/* Mostrar el texto citado del span */}
                    {textoCitado && (
                      <div className="p-3 bg-primary/5 rounded-md border-l-4 border-primary">
                        <div className="flex items-center gap-2 mb-2">
                          <Quote className="h-4 w-4 text-primary" />
                          <span className="text-xs font-semibold text-primary">
                            Texto citado (posiciones {spanStart}-{spanEnd})
                          </span>
                        </div>
                        <p className="text-sm whitespace-pre-wrap">{textoCitado}</p>
                      </div>
                    )}
                    
                    {/* Mostrar cada referencia que respalda este span */}
                    <div className="space-y-3">
                      <div className="text-xs font-semibold text-muted-foreground">
                        Referencias que respaldan este fragmento ({referencias.length}):
                      </div>
                      {referencias.map((ref, refIndex) => {
                        const fileName = ref.source?.split("/").pop() || ref.source || "Fuente desconocida"
                        
                        return (
                          <div key={refIndex} className="p-3 bg-muted rounded-md border">
                            <div className="text-xs text-muted-foreground mb-2">
                              <strong>Fuente #{refIndex + 1}:</strong>
                              <br />
                              <code className="text-xs break-all">{ref.source}</code>
                              <br />
                              <span className="text-xs italic">{fileName}</span>
                            </div>
                            <div className="p-2 bg-background rounded border-l-2 border-muted-foreground mt-2">
                              <pre className="text-xs whitespace-pre-wrap font-mono overflow-x-auto">
                                {ref.content}
                              </pre>
                            </div>
                          </div>
                        )
                      })}
                    </div>
                  </div>
                </AccordionContent>
              </AccordionItem>
            )
          })}
        </Accordion>
      </CardContent>
    </Card>
  )
}

